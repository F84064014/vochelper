import os
import glob
from PyPDF2 import PdfWriter, PdfReader, PdfMerger

def handle(download_dir):

    pdfs = [pdf for pdf in glob.glob(download_dir + "/*")]
    pdf_groups = {}

    def get_doc_type(pdf):
        r = PdfReader(pdf)
        content = r.pages[0].extract_text()
        if "受文者：國軍退除役官兵輔導委員會就養養護處" in content:
            return "cover"
        elif "退 伍 除 役 名 冊" in content:
            return "docA"
        elif "退除給與審定名冊" in content:
            return "docB"
        else:
            return "others"

    def padd_to_enven_page(pdf):
        w = PdfWriter(pdf)
        r = PdfReader(pdf)
        w.append_pages_from_reader(r)

        num_pages = len(r.pages)

        # 如果页数是奇数，添加一页空白页面
        if num_pages % 2 != 0:
            w.add_blank_page()

        w.write(pdf); w.close()

        return

    for pdf in pdfs:
        # pdf: str -> absolute path of pdf
        doc_id = os.path.split(pdf)[-1][:10]

        if not doc_id in pdf_groups:
            pdf_groups[doc_id] = {"cover": None, "docA": None, "docB": None, "others": []}

        pdf_groups[doc_id][get_doc_type(pdf)] = pdf

    final_pdfs = []
    for group in pdf_groups.values():
        for doc_type in ["cover", "docA", "docB"]:
            doc = group[doc_type]
            if doc is not None:
                padd_to_enven_page(doc)
                final_pdfs.append(doc)

    merger = PdfMerger()
    for pdf in final_pdfs:
        merger.append(PdfReader(pdf))
    merger.write(os.path.join(download_dir, "final.pdf"))
    print("successfully write final.pdf")

if __name__=="__main__":
    handle(r"C:\Users\R123828878\Downloads\temp")