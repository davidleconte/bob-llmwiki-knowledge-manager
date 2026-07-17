# Verified Docling Python API recipes

Use the Python API for what the CLI and scripts don't expose: remote VLM
endpoint config, programmatic table/figure access, provenance/bounding boxes,
and custom serialization. All snippets below are the **correct Docling 2.x API**.

> **Common wrong patterns to avoid** (they raise at runtime):
> `DocumentConverter(pipeline_options=...)` (must go through `format_options`);
> `format_options={"pdf": opts}` with string keys (use `InputFormat.PDF`);
> `OcrOptions(use_gpu=...)`; `doc.headings` / `doc.paragraphs`;
> `table.to_markdown()` (it's `export_to_markdown()`); `pic.save()`.

## Configured conversion (standard pipeline)

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

opts = PdfPipelineOptions()
opts.do_ocr = True
opts.do_table_structure = True
opts.table_structure_options.mode = TableFormerMode.ACCURATE   # or .FAST
opts.table_structure_options.do_cell_matching = True
opts.ocr_options.lang = ["en"]                                 # a LIST
opts.accelerator_options = AcceleratorOptions(
    num_threads=4, device=AcceleratorDevice.AUTO,              # AUTO|CPU|CUDA|MPS
)
# enrichments (each pulls a model on first use):
opts.do_code_enrichment = True
opts.do_formula_enrichment = True
opts.do_picture_classification = True

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
)

# Per-call limits live on convert(), NOT the constructor:
result = converter.convert("doc.pdf", max_num_pages=100, max_file_size=50_000_000)
doc = result.document                                          # a DoclingDocument
```

## Exports

```python
doc.export_to_markdown()                        # LLM-friendly Markdown
doc.export_to_markdown(strict_text=True)         # plain text, no markup
doc.export_to_dict()                             # lossless: bbox, hierarchy, confidence
doc.export_to_doctags()                          # DocTags serialization
doc.export_to_html()

from docling_core.types.doc import ImageRefMode
doc.save_as_markdown("out.md", image_mode=ImageRefMode.REFERENCED)  # writes image files
doc.save_as_html("out.html", image_mode=ImageRefMode.EMBEDDED)      # base64 inline
```

## Tables → pandas / CSV / HTML

```python
for i, table in enumerate(doc.tables):
    df = table.export_to_dataframe(doc=doc)      # older versions: export_to_dataframe()
    df.to_csv(f"table_{i}.csv", index=False)
    html = table.export_to_html(doc=doc)
    md = table.export_to_markdown(doc=doc)       # handles merged-cell spans
```

## Figures & page images

Requires image generation to be enabled:

```python
opts.generate_picture_images = True
opts.generate_page_images = True
opts.images_scale = 2.0
# ... convert ...
for i, pic in enumerate(doc.pictures):
    img = pic.get_image(doc)                     # PIL.Image or None
    if img:
        img.save(f"figure_{i}.png")
    print(pic.caption_text(doc))                 # caption if present
for page in doc.pages.values():                  # pages is a dict {page_no: PageItem}
    page.image.pil_image.save(f"page_{page.page_no}.png")
```

## Walk the structure (reading order) + provenance

```python
from docling_core.types.doc import TextItem, TableItem, PictureItem
for item, level in doc.iterate_items():          # depth-first, reading order
    if isinstance(item, TextItem):
        print(item.label, item.text)             # label: title/section_header/text/...
    for prov in item.prov or []:                 # bounding box + page
        print(prov.page_no, prov.bbox)           # bbox: l, t, r, b in page coords
```

## VLM pipeline — local

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel import vlm_model_specs
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

pipe = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,   # or SMOLDOCLING_*, *_MLX, *_VLLM
    generate_page_images=True,
    # force_backend_text=True,   # hybrid: deterministic text, VLM for images/tables
)
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_cls=VlmPipeline, pipeline_options=pipe)
})
doc = converter.convert("paper.pdf").document
```

## VLM pipeline — remote API (CLI cannot configure URL/model/key)

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

vlm_opts = ApiVlmOptions(
    url="http://localhost:8000/v1/chat/completions",           # vLLM / Ollama / LM Studio / hosted
    params=dict(model="ibm-granite/granite-docling-258M", max_tokens=4096),
    headers={"Authorization": "Bearer YOUR_KEY"},              # omit if not needed
    prompt="Convert this page to docling.",
    response_format=ResponseFormat.DOCTAGS,
    timeout=120,
    scale=2.0,
)
pipe = VlmPipelineOptions(
    vlm_options=vlm_opts,
    generate_page_images=True,
    enable_remote_services=True,                               # MANDATORY for any HTTP
)
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_cls=VlmPipeline, pipeline_options=pipe)
})
```

## ASR pipeline — audio / video

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import AsrPipelineOptions
from docling.datamodel import asr_model_specs
from docling.document_converter import DocumentConverter, AudioFormatOption
from docling.pipeline.asr_pipeline import AsrPipeline

pipe = AsrPipelineOptions(asr_options=asr_model_specs.WHISPER_TINY)  # or WHISPER_SMALL/MEDIUM/TURBO
converter = DocumentConverter(format_options={
    InputFormat.AUDIO: AudioFormatOption(pipeline_cls=AsrPipeline, pipeline_options=pipe)
})
transcript = converter.convert("meeting.m4a").document.export_to_markdown()
```

## Choose a PDF backend

```python
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=opts, backend=PyPdfiumDocumentBackend)
})
```

## Version check

```python
from importlib.metadata import version   # docling may not set __version__
print(version("docling"), version("docling-core"))
```
