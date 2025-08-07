import os
import re
import pickle
import numpy as np
from ollama import Client # type: ignore
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
import dateutil.parser
import pytz

LOG_DIR = "/log"
CHUNK_SIZE = 100  # lines per chunk for text logs
CHUNKS_PATH = "/tmp/rag_chunks.pkl"
EMBEDDINGS_PATH = "/tmp/rag_embeddings.npy"
MODEL_NAME_EMBED = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")

ERROR_PATTERNS = [
    r"err", r"error", r"fail", r"exception", r"fatal", r"critical", r"denied", r"rejected",
    r"SQLSTATE", r"syntax error", r"deadlock", r"timeout", r"ORA-", r"mysql", r"mariadb", r"server error",
    r"HTTP [45][0-9][0-9]", r"IIS", r"Apache", r"AADSTS", r"domain error", r"auth fail", r"token expired"
]

# Helper: chunk text logs
def chunk_text_log(filepath, chunk_size=CHUNK_SIZE):
    with open(filepath, "r", errors="ignore") as f:
        lines = f.readlines()
    for i in range(0, len(lines), chunk_size):
        yield ''.join(lines[i:i+chunk_size])

# Helper: chunk EVTX XML logs by <Event> tag
def chunk_evtx_xml(filepath):
    with open(filepath, "r", errors="ignore") as f:
        xml = f.read()
    events = re.findall(r'<Event>.*?</Event>', xml, re.DOTALL)
    for event in events:
        yield event

# Helper: embed text chunks
def embed_chunks(chunks):
    if SentenceTransformer is None:
        raise ImportError("sentence-transformers not installed. Please install it in your container.")
    model = SentenceTransformer(MODEL_NAME_EMBED)
    texts = [chunk for _, chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    np.save(EMBEDDINGS_PATH, embeddings)
    print(f"Saved {len(embeddings)} chunk embeddings to {EMBEDDINGS_PATH}")
    return embeddings

def detect_date_format(lines):
    # Try to infer date format from first 10 lines
    opts_list = [(False, True), (True, False), (True, True), (False, False)]
    scores = {opts: 0 for opts in opts_list}
    for line in lines:
        ts = line.split()[0]
        for opts in opts_list:
            try:
                dateutil.parser.parse(ts, dayfirst=opts[0], yearfirst=opts[1])
                scores[opts] += 1
            except Exception:
                continue
    # Pick the format with most successful parses
    best_opts = max(scores, key=scores.get)
    return best_opts

def extract_timestamp(line, opts):
    # Try to find a timestamp anywhere in the line using regex
    ts_match = re.search(r'(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)', line)
    if ts_match:
        ts = ts_match.group(1)
    else:
        # Fallback: use first token
        ts = line.split()[0]
    try:
        dt = dateutil.parser.parse(ts, dayfirst=opts[0], yearfirst=opts[1])
        if dt.tzinfo is None:
            dt_utc = pytz.UTC.localize(dt)
        else:
            dt_utc = dt.astimezone(pytz.UTC)
        return ts, dt_utc, f"regex+dayfirst={opts[0]},yearfirst={opts[1]}"
    except Exception:
        return ts, None, "unparsed"

# Pre-chunk all logs, embed, and save to disk
def pre_chunk_logs():
    all_lines = []
    for fname in os.listdir(LOG_DIR):
        path = os.path.join(LOG_DIR, fname)
        # Only process .txt and .log files, including converted EVTX and MTA
        if not (fname.endswith('.txt') or fname.endswith('.log')):
            continue
        with open(path, "r", errors="ignore") as fin:
            lines = fin.readlines()
        # Detect date format from first 10 lines
        best_opts = detect_date_format(lines[:10])
        for line in lines:
            orig_ts, utc_ts, parse_info = extract_timestamp(line, best_opts)
            error_flag = ""
            for pat in ERROR_PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    error_flag = "[ERROR]"
                    break
            # Annotate with source file, original and UTC timestamp, parse info, error flag
            if utc_ts:
                annotated = f"[{fname}] [ORIG_TS: {orig_ts}] [UTC_TS: {utc_ts.isoformat()}] [PARSE: {parse_info}] {error_flag} {line.strip()}"
                all_lines.append((utc_ts, annotated))
            else:
                annotated = f"[{fname}] [NO_TS] [PARSE: {parse_info}] {error_flag} {line.strip()}"
                all_lines.append((None, annotated))
    # Sort lines by UTC timestamp, None at the end
    all_lines.sort(key=lambda x: (x[0] is None, x[0]))
    # Chunk sorted lines
    chunks = []
    lines = [l[1] for l in all_lines]
    for i in range(0, len(lines), CHUNK_SIZE):
        chunk = '\n'.join(lines[i:i+CHUNK_SIZE])
        chunks.append(("time_ordered_logs", chunk))
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)
    print(f"Pre-chunked {len(chunks)} time-ordered log chunks saved to {CHUNKS_PATH}")
    embed_chunks(chunks)

# Load pre-chunked logs
def load_chunks():
    with open(CHUNKS_PATH, "rb") as f:
        return pickle.load(f)

# Load chunk embeddings
def load_embeddings():
    return np.load(EMBEDDINGS_PATH)

# Query LLM for top-k similar chunks and aggregate results
def analyze_chunks(question, top_k=10):
    import time
    if SentenceTransformer is None:
        raise ImportError("sentence-transformers not installed. Please install it in your container.")
    client = Client()
    chunks = load_chunks()
    embeddings = load_embeddings()
    model = SentenceTransformer(MODEL_NAME_EMBED)
    q_emb = model.encode([question])[0]
    scores = np.dot(embeddings, q_emb) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(q_emb) + 1e-8)
    top_idx = np.argsort(scores)[-top_k:][::-1]
    grouped_results = {}
    print(f"Selected top {top_k} relevant chunks for query.")
    for rank, idx in enumerate(top_idx, 1):
        fname, chunk = chunks[idx]
        print(f"Processing chunk {rank}/{top_k} ({fname})")
        start = time.time()
        prompt = f"Analyze the following log chunk for errors, outages, and answer the question.\n\nLog chunk from {fname}:\n{chunk}\n\nQuestion: {question}\nList all findings with timestamps and details."
        response = client.generate(model=os.environ.get("MODEL_NAME", "granite3-moe:3b"), prompt=prompt)
        elapsed = time.time() - start
        print(f"Chunk {rank} processed in {elapsed:.2f}s.")
        if fname not in grouped_results:
            grouped_results[fname] = []
        grouped_results[fname].append(response['response'].strip())
    print(f"\nAnalysis complete. Processed {top_k} chunks.")
    # Format output grouped by log file
    output = []
    for fname, responses in grouped_results.items():
        output.append(f"=== {fname} ===\n" + "\n---\n".join(responses) + "\n")
    with open("/tmp/rag_result.txt", "w") as f:
        f.write('\n'.join(output))
    return '\n'.join(output)

# CLI
if __name__ == "__main__":
    if not os.path.exists(CHUNKS_PATH) or not os.path.exists(EMBEDDINGS_PATH):
        pre_chunk_logs()
    print("RAG CLI ready. Type 'ask <question>' or 'exit'. (Vector search, high-accuracy mode)")
    while True:
        cmd = input("rag> ").strip()
        if cmd == "exit":
            break
        elif cmd.startswith("ask "):
            question = cmd[4:].strip()
            if question:
                print(analyze_chunks(question, top_k=10))
            else:
                print("Usage: ask <your question>")
        else:
            print("Commands: ask <question> | exit")
