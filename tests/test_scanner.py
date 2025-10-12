import os
from scrubber.core import StorageScrubber, FileInfo


def test_scan_empty(tmp_path):
    ss = StorageScrubber(root=str(tmp_path))
    res = ss.scan()
    assert res == []


def test_classify_temp_file(tmp_path):
    p = tmp_path / "test.tmp"
    p.write_text("hello")
    ss = StorageScrubber(root=str(tmp_path))
    res = ss.scan()
    assert len(res) == 1
    assert ss.classify(res[0]) == 'temp'


def test_duplicates_and_top(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    c = tmp_path / "big.bin"
    a.write_text("same")
    b.write_text("same")
    c.write_bytes(b"0" * 10240)
    ss = StorageScrubber(root=str(tmp_path))
    res = ss.scan()
    # compute hashes and find duplicates
    groups = ss.find_duplicates(res)
    # there should be one duplicate group for a and b
    assert any(len(g) == 2 for g in groups)
    top = ss.top_files(res, n=1)
    assert len(top) == 1
    assert top[0].size >= 10240


def test_exclude_and_auto_clean(tmp_path):
    # create structure with node_modules and normal dir
    nm = tmp_path / "node_modules" / "m" / "file.js"
    nm.parent.mkdir(parents=True, exist_ok=True)
    nm.write_text("console.log('x')")
    keep = tmp_path / "keep" / "keep.txt"
    keep.parent.mkdir(parents=True, exist_ok=True)
    keep.write_text("stay")

    ss = StorageScrubber(root=str(tmp_path))
    all_files = ss.scan()
    cand = ss.select_auto_clean(all_files)
    # node_modules file should be a candidate
    assert any('node_modules' in f.path for f in cand)

    # exclude node_modules and scan again
    all_files2 = ss.scan(exclude_patterns=['node_modules'])
    assert not any('node_modules' in f.path for f in all_files2)


def test_permanent_delete_simulation(tmp_path):
    f = tmp_path / "trash.txt"
    f.write_text("deleteme")
    ss = StorageScrubber(root=str(tmp_path))
    files = ss.scan()
    # call delete_files with permanent=True but don't actually remove system files
    # the method will try to remove the file; ensure no exception
    ss.delete_files(files, confirm=True, interactive=False, permanent=True)
    # file should no longer exist
    assert not f.exists()
