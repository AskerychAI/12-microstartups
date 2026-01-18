#!/usr/bin/env python3
"""
Generate embeddings for Hugo site content.
This script processes all markdown files and generates embeddings using sentence-transformers.
"""

import os
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("Error: sentence-transformers and numpy are required.")
    print("Install them with: pip install sentence-transformers numpy")
    sys.exit(1)


def extract_markdown_content(md_file: Path) -> Dict[str, Any]:
    """
    Extract title and content from markdown file.
    
    Returns dict with:
    - title: page title
    - content: plain text content (without frontmatter)
    - url: relative URL path
    """
    content = md_file.read_text(encoding='utf-8')
    
    # Extract frontmatter if present
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        # Extract title from frontmatter
        title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', frontmatter_text, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
    else:
        body = content
        title = md_file.stem
    
    # Clean markdown: remove headers, links, images, code blocks
    # Keep only plain text for embeddings
    text = body
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    # Remove headers (#, ##, etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Generate URL from file path
    # content/posts/article.md -> /posts/article/
    # content/pages/page.md -> /pages/page/
    relative_path = md_file.relative_to(Path('content'))
    url_parts = relative_path.parts[:-1]  # Remove filename
    url = '/' + '/'.join(url_parts) + '/' + relative_path.stem + '/'
    
    return {
        'title': title,
        'content': text,
        'url': url
    }


def process_hugo_content(content_dir: Path, model: SentenceTransformer) -> Dict[str, Dict[str, Any]]:
    """
    Process all markdown files in content directory and generate embeddings.
    
    Returns dict with structure:
    {
        "/posts/article/": {
            "title": "...",
            "url": "/posts/article/",
            "content": "...",
            "embedding": [0.12, 0.34, ...]
        }
    }
    """
    embeddings_data = {}
    
    # Find all markdown files
    md_files = list(content_dir.rglob('*.md'))
    
    # Filter out special files
    excluded_patterns = ['_index.md', '404.md']
    md_files = [f for f in md_files if f.name not in excluded_patterns]
    
    print(f"Found {len(md_files)} markdown files to process...")
    
    # Extract texts for batch processing
    texts = []
    metadata = []
    
    for md_file in md_files:
        try:
            data = extract_markdown_content(md_file)
            
            # Skip if content is empty
            if not data['content']:
                continue
            
            # Combine title and content for embedding
            text_for_embedding = f"{data['title']} {data['content']}"
            
            texts.append(text_for_embedding)
            metadata.append(data)
            
        except Exception as e:
            print(f"Warning: Error processing {md_file}: {e}", file=sys.stderr)
            continue
    
    if not texts:
        print("Warning: No content found to process!")
        return embeddings_data
    
    # Generate embeddings in batches for efficiency
    print(f"Generating embeddings for {len(texts)} documents...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    
    # Convert numpy arrays to lists and store
    for i, (meta, embedding) in enumerate(zip(metadata, embeddings)):
        url = meta['url']
        embeddings_data[url] = {
            'title': meta['title'],
            'url': url,
            'content': meta['content'],
            'embedding': embedding.tolist()
        }
    
    print(f"Generated embeddings for {len(embeddings_data)} documents.")
    return embeddings_data


def main():
    """Main function."""
    # Determine paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    content_dir = project_dir / 'content'
    output_file = project_dir / 'static' / 'embeddings.json'
    
    # Check content directory exists
    if not content_dir.exists():
        print(f"Error: Content directory not found: {content_dir}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load model (use multilingual model for Russian support)
    print("Loading sentence-transformers model...")
    model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("The model will be downloaded on first use. This may take a few minutes...")
        sys.exit(1)
    
    # Process content and generate embeddings
    embeddings_data = process_hugo_content(content_dir, model)
    
    # Save to JSON
    print(f"Saving embeddings to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    print(f"✓ Embeddings saved successfully! File size: {file_size:.2f} MB")
    print(f"  Total documents: {len(embeddings_data)}")
    print(f"  Output file: {output_file}")


if __name__ == '__main__':
    main()
