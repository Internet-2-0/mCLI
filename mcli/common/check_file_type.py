from msdk.utils.file_utils import is_elf_file, is_document_file, is_windows_pe_file


def is_pe(filename):
    return is_windows_pe_file(filename)


def is_ms_doc(filename):
    return is_document_file(filename)


def is_elf(filename):
    return is_elf_file(filename)
