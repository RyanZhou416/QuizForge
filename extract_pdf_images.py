#!/usr/bin/env python3
"""
PDF图片提取脚本
用法: python extract_pdf_images.py "PDF路径" "输出目录"
"""

import sys
import os
import fitz  # PyMuPDF

def extract_images(pdf_path, output_dir):
    """从PDF中提取所有图片"""
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建目录: {output_dir}")
    
    # 打开PDF
    doc = fitz.open(pdf_path)
    image_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # 生成文件名
                image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                # 保存图片
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                image_count += 1
                print(f"提取: {image_filename} (页面 {page_num + 1})")
                
            except Exception as e:
                print(f"警告: 无法提取页面 {page_num + 1} 的图片 {img_index + 1}: {e}")
    
    doc.close()
    print(f"\n完成! 共提取 {image_count} 张图片到 {output_dir}")
    return image_count

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python extract_pdf_images.py <PDF路径> <输出目录>")
        print("示例: python extract_pdf_images.py ceg3156BML1.pdf images/ch01")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(pdf_path):
        print(f"错误: PDF文件不存在: {pdf_path}")
        sys.exit(1)
    
    extract_images(pdf_path, output_dir)
