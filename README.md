# copyast

`copyast` là CLI tool dùng để export source code dạng text vào một file bundle duy nhất, sau đó cho phép import, update, delete và sync bundle đó theo thay đổi của Git.

---

## 1. Yêu cầu

- Python 3.11 trở lên

Project hiện khai báo trong `pyproject.toml`:

```toml
requires-python = ">=3.11"
````

---

## 2. Cài đặt

### 2.1 Cách khuyên dùng: editable install

Tại thư mục root của project:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

Sau khi cài xong,  có thể chạy:

```bash
copyast --help
```

Project đã khai báo console script:

```toml
[project.scripts]
copyast = "app.main:main"
```

nên sau `pip install -e .` không cần gọi `python -m ...` nữa.

---

### 2.2 Chạy nhanh khi chưa cài editable

Project đang dùng `src` layout, nên nếu chưa chạy `pip install -e .`, có thể chạy:

```bash
PYTHONPATH=src python -m app.main --help
```

hoặc:

```bash
cd src
python -m app.main --help
```

Đây là cách phù hợp để test nhanh.

---

## 3. Cấu trúc bundle

Mỗi file trong bundle sẽ được lưu theo block:

```txt
 === FILE: path/to/file.py ===
<file content>

 === FILE: another/file.txt ===
<file content>
```

---

## 4. Các command hiện có

* `export`
* `import`
* `bulk-import`
* `delete`
* `bulk-delete`
* `scan-delete`
* `sync-git`

---

## 5. Cách dùng chi tiết

### 5.1 Export toàn bộ source vào bundle

Ví dụ:

```bash
copyast export \
  --root . \
  --output ./copyast-output.txt \
  --ignore '.idea/' \
  --ignore '.git/' \
  --ignore '.env' \
  --ignore-file '.gitignore'
```

### Ý nghĩa

* `--root`: thư mục project gốc
* `--output`: file bundle đầu ra
* `--ignore`: thêm pattern ignore bằng tay
* `--ignore-file`: chỉ định file ignore bổ sung

### Cách hoạt động

Khi export, `copyast` sẽ:

* duyệt tất cả file trong `root`
* bỏ qua file output của chính nó
* bỏ qua file bị ignore
* bỏ qua binary file
* đọc file text và ghi vào bundle

---

### 5.2 Import một file vào bundle

```bash
copyast import \
  --root . \
  --bundle ./copyast-output.txt \
  --path src/app/main.py
```

Lệnh này sẽ:

* load bundle hiện tại
* đọc file `src/app/main.py`
* nếu entry đã có thì update
* nếu chưa có thì thêm mới

---

### 5.3 Import nhiều file

#### Truyền trực tiếp

```bash
copyast bulk-import \
  --root . \
  --bundle ./copyast-output.txt \
  --paths src/app/main.py src/app/domain/services.py tests/test_smoke.py
```

#### Truyền qua file list

Ví dụ `files.txt`:

```txt
src/app/main.py
src/app/domain/services.py
tests/test_smoke.py
```

rồi chạy:

```bash
copyast bulk-import \
  --root . \
  --bundle ./copyast-output.txt \
  --list-file ./files.txt
```

---

### 5.4 Delete một file khỏi bundle

```bash
copyast delete \
  --bundle ./copyast-output.txt \
  --path src/app/main.py
```

Lệnh này chỉ xóa entry khỏi bundle, không xóa file thật ngoài filesystem.

---

### 5.5 Delete nhiều file khỏi bundle

#### Truyền trực tiếp

```bash
copyast bulk-delete \
  --bundle ./copyast-output.txt \
  --paths src/app/main.py tests/test_smoke.py
```

#### Truyền qua file list

```bash
copyast bulk-delete \
  --bundle ./copyast-output.txt \
  --list-file ./files-to-delete.txt
```

---

### 5.6 Delete theo substring trong path

```bash
copyast scan-delete \
  --bundle ./copyast-output.txt \
  --contains 'tests/'
```

Lệnh trên sẽ xóa mọi block có path chứa `tests/`.

---

### 5.7 Sync bundle theo Git

```bash
copyast sync-git \
  --root . \
  --bundle ./copyast-output.txt
```

Lệnh này sẽ:

* kiểm tra thư mục có phải Git repo không
* đọc `git status --porcelain`
* import/update các file modified và untracked
* xóa các file deleted khỏi bundle

---

## 6. Ignore rules

`copyast` hiện hỗ trợ ignore từ:

* file ignore riêng qua `--ignore-file`
* `.gitignore`
* pattern thêm bằng `--ignore`

### Ví dụ `.copyastignore`

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
env/

build/
dist/
*.egg-info/
.eggs/

.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

.vscode/
.idea/
*.iml

.env
.env.*

bundle.txt
*.bundle.txt
*.png
*.jpg
*.pdf
*.zip
```

Project hiện cũng có `.copyastignore.example` để làm mẫu.  có thể copy file đó thành `.copyastignore` rồi mở rộng thêm rule riêng cho project của mình.

## Cleanup Code (Optional)

```shell
pip install black isort ruff
ruff check . --fix
isort .
black .
``` 

---
