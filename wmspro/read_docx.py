import zipfile
import xml.etree.ElementTree as ET

def run():
    docx_path = "/home/erpadmin/bench-wmspro/ILS_Freight_Transportation_Documentation.docx"
    try:
        with zipfile.ZipFile(docx_path) as z:
            doc_xml = z.read("word/document.xml")
            root = ET.fromstring(doc_xml)
            
            # Docx XML Namespace
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            paragraphs = []
            for p in root.findall('.//w:p', ns):
                texts = []
                for t in p.findall('.//w:t', ns):
                    if t.text:
                        texts.append(t.text)
                paragraphs.append("".join(texts))
            
            # Print paragraph by paragraph
            content = "\n".join(p for p in paragraphs if p.strip())
            with open("docx_content.txt", "w") as f:
                f.write(content)
            print("Successfully written to docx_content.txt")
    except Exception as e:
        print(f"Error: {e}")
