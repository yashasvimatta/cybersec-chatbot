"""
Local File Handler
Reads documents from local folder instead of Google Drive
Supports: PDF, Word, Excel, PowerPoint, CSV, TXT, and more
"""

import os
from typing import List, Dict
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
import pandas as pd
from pathlib import Path


class LocalFileHandler:
    def __init__(self, base_folder: str = "kb_raw"):
        """
        Initialize with base folder path
        Args:
            base_folder: Path to your knowledge base folder (default: kb_raw)
        """
        self.base_folder = base_folder
        
        # Check if folder exists
        if not os.path.exists(base_folder):
            print(f"⚠️  Warning: Folder '{base_folder}' does not exist")
            print(f"   Creating folder: {base_folder}")
            os.makedirs(base_folder)
        else:
            print(f"✓ Found knowledge base folder: {base_folder}")
    
    def fetch_all_documents(self, folder_path: str = None) -> List[Dict]:
        """
        Recursively fetch all documents from local folder
        Returns list of document dictionaries with content and metadata
        
        Args:
            folder_path: Optional subfolder path (relative to base_folder)
        """
        if folder_path is None:
            folder_path = self.base_folder
        else:
            folder_path = os.path.join(self.base_folder, folder_path)
        
        all_documents = []
        self._recursive_fetch(folder_path, all_documents)
        
        print(f"\n✓ Found {len(all_documents)} documents")
        return all_documents
    
    def _recursive_fetch(self, folder_path: str, documents: List[Dict], relative_path: str = ""):
        """Recursively fetch files from folder and subfolders"""
        try:
            # List all items in folder
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                current_path = os.path.join(relative_path, item) if relative_path else item
                
                # Skip hidden files and __MACOSX folders
                if item.startswith('.') or item == '__MACOSX':
                    continue
                
                # If it's a folder, recurse into it
                if os.path.isdir(item_path):
                    print(f"📁 Scanning folder: {current_path}")
                    self._recursive_fetch(item_path, documents, current_path)
                
                # If it's a file, process it
                else:
                    print(f"📄 Processing: {current_path}")
                    doc_content = self._extract_content(item_path, item)
                    
                    if doc_content:
                        documents.append({
                            'id': item_path,  # Use file path as unique ID
                            'name': item,
                            'path': current_path,
                            'content': doc_content,
                            'mimeType': self._get_mime_type(item),
                            'modifiedTime': os.path.getmtime(item_path)
                        })
        
        except Exception as e:
            print(f"Error fetching from folder {folder_path}: {str(e)}")
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from file extension"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.md': 'text/markdown',
            '.json': 'application/json',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _extract_content(self, file_path: str, filename: str) -> str:
        """Extract text content from different file types"""
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            # PDF files
            if ext == '.pdf':
                return self._extract_pdf(file_path)
            
            # Word documents
            elif ext in ['.docx', '.doc']:
                return self._extract_docx(file_path)
            
            # Excel files
            elif ext in ['.xlsx', '.xls']:
                return self._extract_excel(file_path)
            
            # PowerPoint
            elif ext in ['.pptx', '.ppt']:
                return self._extract_pptx(file_path)
            
            # CSV files
            elif ext == '.csv':
                return self._extract_csv(file_path)
            
            # Plain text files
            elif ext in ['.txt', '.md', '.json', '.log']:
                return self._extract_text(file_path)
            
            else:
                print(f"  ⚠  Unsupported file type: {ext}")
                return ""
        
        except Exception as e:
            print(f"  ✗ Error extracting content: {str(e)}")
            return ""
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"  ✗ PDF extraction error: {str(e)}")
            return ""
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
            
            return text
        except Exception as e:
            print(f"  ✗ Word extraction error: {str(e)}")
            return ""
    
    def _extract_excel(self, file_path: str) -> str:
        """Extract text from Excel files"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text = ""
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                text += f"\n--- Sheet: {sheet_name} ---\n"
                text += df.to_string(index=False) + "\n"
            
            return text
        except Exception as e:
            print(f"  ✗ Excel extraction error: {str(e)}")
            return ""
    
    def _extract_pptx(self, file_path: str) -> str:
        """Extract text from PowerPoint presentations"""
        try:
            prs = Presentation(file_path)
            text = ""
            
            for slide_num, slide in enumerate(prs.slides, 1):
                text += f"\n--- Slide {slide_num} ---\n"
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            
            return text
        except Exception as e:
            print(f"  ✗ PowerPoint extraction error: {str(e)}")
            return ""
    
    def _extract_csv(self, file_path: str) -> str:
        """Extract text from CSV files"""
        try:
            df = pd.read_csv(file_path)
            return df.to_string(index=False)
        except Exception as e:
            print(f"  ✗ CSV extraction error: {str(e)}")
            return ""
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            print(f"  ✗ Could not decode text file with common encodings")
            return ""
        except Exception as e:
            print(f"  ✗ Text extraction error: {str(e)}")
            return ""
    
    def check_connection(self) -> bool:
        """Check if folder exists and is accessible"""
        return os.path.exists(self.base_folder) and os.path.isdir(self.base_folder)
    
    def get_folder_stats(self) -> Dict:
        """Get statistics about the knowledge base folder"""
        stats = {
            'total_files': 0,
            'total_folders': 0,
            'file_types': {},
            'total_size_mb': 0
        }
        
        for root, dirs, files in os.walk(self.base_folder):
            stats['total_folders'] += len(dirs)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                stats['total_files'] += 1
                
                # Count file types
                ext = os.path.splitext(file)[1].lower()
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                # Calculate size
                file_path = os.path.join(root, file)
                stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
        
        return stats


if __name__ == "__main__":
    # Test the handler
    print("Testing Local File Handler")
    print("=" * 50)
    
    handler = LocalFileHandler("kb_raw")
    
    if handler.check_connection():
        print("\n✓ Folder is accessible")
        
        stats = handler.get_folder_stats()
        print(f"\nFolder Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total folders: {stats['total_folders']}")
        print(f"  Total size: {stats['total_size_mb']:.2f} MB")
        print(f"  File types: {dict(stats['file_types'])}")
        
        # Test document fetching
        print("\n" + "=" * 50)
        print("Fetching documents...")
        docs = handler.fetch_all_documents()
        
        if docs:
            print(f"\n✓ Successfully processed {len(docs)} documents")
            print(f"\nSample document:")
            print(f"  Name: {docs[0]['name']}")
            print(f"  Path: {docs[0]['path']}")
            print(f"  Content length: {len(docs[0]['content'])} characters")
            print(f"  Preview: {docs[0]['content'][:200]}...")
        else:
            print("\n⚠  No documents found. Add some files to kb_raw folder!")
    else:
        print("\n✗ Folder not accessible")
