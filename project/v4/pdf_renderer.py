from pathlib import Path
import re,html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether,PageBreak
from reportlab.lib.pagesizes import A4
PAPER=Path(__file__).resolve().parent/"paper"
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
styles={
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10,leading=15,spaceAfter=7,allowWidows=0,allowOrphans=0,textColor=colors.HexColor('#203041')),
 'title':ParagraphStyle('title',fontName='Arial-Bold',fontSize=21,leading=28,spaceAfter=17,textColor=colors.HexColor('#143d48')),
 'h2':ParagraphStyle('h2',fontName='Arial-Bold',fontSize=14,leading=19,spaceBefore=15,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#176760')),
 'h3':ParagraphStyle('h3',fontName='Arial-Bold',fontSize=11,leading=16,spaceBefore=10,spaceAfter=6,keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=8,leading=11,spaceAfter=0),
 'caption':ParagraphStyle('caption',fontName='Arial-Italic',fontSize=8.5,leading=12,spaceAfter=10,textColor=colors.HexColor('#63717d'))}
def inline(s):
 s=html.escape(s).replace('–','-').replace('—','-').replace('‑','-')
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'\1',s)
 s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#176760">\1</link>',s)
 return s
def build_pdf(md,out,title):
 lines=md.splitlines();story=[];i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    fields=[v.strip() for v in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r'[-: ]+',v) for v in fields):rows.append([Paragraph(inline(v),styles['cell']) for v in fields])
    i+=1
   widths=([126]+[58]*6) if len(rows[0])==7 else ([105,215,165] if len(rows[0])==3 and 'xử lý' in rows[0][1].getPlainText() else ([155,60,270] if len(rows[0])==3 and rows[0][1].getPlainText()=='Số lượng' else ([170,100,215] if len(rows[0])==3 else None)))
   table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT');table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3eeec')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#588e88')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#dde4e8'))]));story.extend([KeepTogether([table,Spacer(1,10)])] if len(rows)<=12 else [table,Spacer(1,10)]);continue
  image_match=re.match(r'!\[(.*?)\]\((.*?)\)',line)
  if image_match:
   p=(PAPER/image_match.group(2)).resolve()
   if p.exists():
    from PIL import Image as PILImage
    with PILImage.open(p) as im:width,height=im.size
    scale=min(475/width,370/height);story.append(Image(str(p),width*scale,height*scale));story.append(Spacer(1,8))
   i+=1;continue
  if line=='## Tài liệu tham khảo':story.append(PageBreak())
  if line.startswith('# '):style=styles['title'];content=line[2:]
  elif line.startswith('## '):style=styles['h2'];content=line[3:]
  elif line.startswith('### '):style=styles['h3'];content=line[4:]
  else:
   style=styles['caption'] if line.startswith('Hình ') else styles['body'];content=line
   while i+1<len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|','![')) and not re.match(r'^\d+\. ',lines[i+1]):
    i+=1;content+=' '+lines[i].strip()
  story.append(Paragraph(inline(content),style));i+=1
 def footer(c,doc):
  c.setStrokeColor(colors.HexColor('#d8e1e6'));c.line(48,38,A4[0]-48,38);c.setFont('Arial',8);c.setFillColor(colors.HexColor('#71808e'));c.drawString(48,25,title);c.drawRightString(A4[0]-48,25,str(doc.page))
 doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=45,bottomMargin=53,title=title,author='Research working draft');doc.build(story,onFirstPage=footer,onLaterPages=footer)
