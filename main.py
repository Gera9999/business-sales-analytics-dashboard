from __future__ import annotations

import shutil
from pathlib import Path

from dashboard.plotly_dashboard import save_dashboard_html
from src.pipeline import run_pipeline


def _ensure_dataset(project_root: Path) -> Path:
    """Ensure the dataset exists at data/train.csv.

    The source dataset is train.csv at the repository root.
    """

    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    target = data_dir / "train.csv"
    if target.exists():
        return target

    source = project_root / "train.csv"
    if source.exists():
        shutil.copyfile(source, target)
        return target

    raise FileNotFoundError(
        "train.csv was not found at the project root. Place the file in the repository root."
    )


def main() -> None:
    project_root = Path(__file__).resolve().parent
    dataset_path = _ensure_dataset(project_root)

    artifacts = run_pipeline(dataset_path)

    output_path = project_root / "output" / "sales_dashboard.html"
    saved = save_dashboard_html(artifacts, output_path)

    # Optional: copy to docs/ for GitHub Pages hosting
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    shutil.copyfile(saved, docs_dir / "index.html")

    print(f"Dashboard saved to: {saved}")
    print(f"GitHub Pages file updated: {docs_dir / 'index.html'}")


if __name__ == "__main__":
    main()
