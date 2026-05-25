# 🤖 MiMo Form Agent

# 🔍 MiMo Code Reviewer

AI-powered code review agent using **Xiaomi MiMo V2.5 Pro**. Scans Python files and generates actionable improvement suggestions.

## Features

- 🐛 Bug detection & security issues
- ⚡ Performance optimization suggestions  
- 📝 Code style & readability improvements
- 📊 Markdown report output

## Usage

```bash
pip install requests
export MIMO_API_KEY="your-key"

# Review a single file
python review.py app.py

# Review entire project
python review.py ./src --recursive

# Output as markdown report
python review.py app.py --output report.md
```

## Example Output

```
📁 Reviewing: app.py (142 lines)

🐛 [Bug] Line 23: Unchecked None return from database query
   → Add null check before accessing .data attribute

⚡ [Perf] Line 67: Using list comprehension inside loop
   → Move filtering outside the loop to reduce O(n²) complexity

📝 [Style] Line 89: Function exceeds 40 lines
   → Extract validation logic into separate helper function

Score: 7.2/10 | Issues: 3 | Suggestions: 3
```

## How it works

1. Reads Python source files
2. Sends code chunks to MiMo V2.5 Pro for analysis
3. Parses structured review output (bugs, perf, style)
4. Generates formatted report

Built with Xiaomi MiMo V2.5 Pro 🚀

