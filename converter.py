"""Orchestration layer over the plugin core (spec PC-1/PC-8/PC-9).

OptimizedMediaConverter keeps the exact public API the UI depends on, but
execution now flows through the registry: file type is detected by signature
(core.detect), inputs are turned into an ImageSet by registered decoders, and
outputs are produced by registered encoders. Adding a format no longer means
editing this class — it means registering a handler module.

Discovery (find_comics) stays here: it enumerates which sources are conversion
targets, independent of how each is decoded.
"""
import os
from pathlib import Path

from core.detect import detect_path
from core.intermediates import ImageSet
from core.loader import load_base_modules
from core.registry import registry
from core.utils import IMAGE_EXTENSIONS, natural_sort_key, unique_path

load_base_modules()


class ImageGroup:
    """A virtual target: a set of loose image files combined into one document."""
    def __init__(self, images, name):
        self.images = images
        self.name = name
        self.stem = name

    # Quack like a Path for the parts of the pipeline that inspect targets.
    suffix = ''

    def is_file(self):
        return False

    def is_dir(self):
        return False


class OptimizedMediaConverter:
    def __init__(self):
        self.valid_extensions = IMAGE_EXTENSIONS

    @staticmethod
    def _natural_sort_key(s):
        return natural_sort_key(s)

    @staticmethod
    def _unique_path(path):
        return unique_path(path)

    def find_comics(self, source_paths, cancel_check=None):
        """Scans a list of paths (files or directories) and returns a list of targets."""
        targets = set()  # Use set to avoid duplicates
        loose_images = {}  # parent dir -> list of loose image files, grouped into one doc each

        for path_str in source_paths:
            if cancel_check and cancel_check():
                raise InterruptedError("Операция прервана")
            source = Path(path_str)
            if not source.exists():
                continue

            if source.is_file():
                ext = source.suffix.lower()
                if ext in ('.zip', '.cbz', '.pdf'):
                    targets.add(source)
                elif ext in self.valid_extensions:
                    loose_images.setdefault(source.parent, []).append(source)
            elif source.is_dir():
                for root, dirs, files in os.walk(source):
                    if cancel_check and cancel_check():
                        raise InterruptedError("Операция прервана")

                    # Single pass: collect archives/PDFs and note any image in this dir.
                    has_images = False
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in ('.zip', '.cbz', '.pdf'):
                            targets.add(Path(root) / f)
                        elif ext in self.valid_extensions:
                            has_images = True
                    if has_images:
                        targets.add(Path(root))

        # Turn each group of loose images into one virtual target named after its folder.
        for parent, imgs in loose_images.items():
            imgs.sort(key=lambda x: natural_sort_key(x.name))
            targets.add(ImageGroup(imgs, parent.name or "Images"))

        # Sort targets by name for consistent ordering
        sorted_targets = list(targets)
        sorted_targets.sort(key=lambda x: natural_sort_key(x.name))
        return sorted_targets

    def extract_and_prepare(self, source_path, cancel_check=None):
        """Decode a target into (image_paths, temp_dir) via the registry."""
        if isinstance(source_path, ImageGroup):
            # Loose images are already on disk; just hand back the (sorted) list.
            return list(source_path.images), None

        source = Path(source_path)

        if source.is_dir():
            img_set = registry.decoder_for("dir").decode(source, cancel_check)
            return img_set.pages, img_set.temp_dir

        source_type = detect_path(source)
        decoder = registry.decoder_for(source_type) if source_type else None
        if decoder is None:
            raise ValueError(f"Неизвестный тип источника: {source.name}")

        img_set = decoder.decode(source, cancel_check)
        return img_set.pages, img_set.temp_dir

    def cleanup(self, temp_dir):
        import shutil
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

    # --- output: thin wrappers over registered encoders ---------------------

    def _encode(self, format_id, images, filename, output_dir, base_dir=None,
                cancel_check=None):
        img_set = ImageSet(pages=images, name=filename, base_dir=base_dir)
        return registry.encoder_for(format_id).build(
            img_set, filename, output_dir, cancel_check=cancel_check)

    def to_cbz(self, images, filename, output_dir, base_dir=None, cancel_check=None):
        return self._encode("cbz", images, filename, output_dir, base_dir, cancel_check)

    def to_zip(self, images, filename, output_dir, base_dir=None, cancel_check=None):
        return self._encode("zip", images, filename, output_dir, base_dir, cancel_check)

    def to_pdf(self, images_paths, filename, output_dir, cancel_check=None):
        return self._encode("pdf", images_paths, filename, output_dir,
                            cancel_check=cancel_check)
