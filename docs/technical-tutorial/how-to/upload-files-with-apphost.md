# Apphost file uploads

You can always skip defining `payload` in a Practicus AI apphost API handler and use `Starlette Request` object instead.

This can be used for file uploads, handling streaming requests and more.

## Handling file uploads

```python
from pathlib import Path
from starlette.requests import Request
from starlette.responses import JSONResponse

import practicuscore as prt


@prt.api("/upload-file", spec=api_spec)
async def handle_upload_file(request: Request):
    form = await request.form()  # parses multipart/form-data
    upload_file = form.get("file")  # name="file" in the HTML form

    if upload_file is None:
        return JSONResponse({"error": "missing form field 'file'"}, status_code=400)

    # Starlette UploadFile
    filename: str = upload_file.filename or "unknown"
    content_type: str = upload_file.content_type or "application/octet-stream"

    # read bytes (ok for small/medium files)
    file_bytes: bytes = await upload_file.read()

    return JSONResponse(
        {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
        }
    )


# Save upload to disk without loading whole file into memory

@prt.api("/upload-file2", spec=api_spec)
async def handle_upload_file2(request: Request) -> JSONResponse:
    form = await request.form()
    upload_file = form.get("file")
    if upload_file is None:
        return JSONResponse({"error": "missing form field 'file'"}, status_code=400)

    uploads_dir: Path = Path("/tmp/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_name: str = (upload_file.filename or "upload.bin").replace("/", "_")
    target_path: Path = uploads_dir / safe_name

    bytes_written: int = 0
    with target_path.open("wb") as output_fp:
        while True:
            chunk: bytes = await upload_file.read(1024 * 1024)  # 1 MiB
            if not chunk:
                break
            output_fp.write(chunk)
            bytes_written += len(chunk)

    return JSONResponse({"saved_as": str(target_path), "size_bytes": bytes_written})
```


---

**Previous**: [Share Workers](share-workers.md) | **Next**: [Use Custom Metrics](use-custom-metrics.md)
