from msdk.utils.file_utils import is_elf_file, is_document_file, is_windows_pe_file


# these are pretty self explanatory

def is_pe(filename):
    return is_windows_pe_file(filename)


def is_ms_doc(filename):
    return is_document_file(filename)


def is_elf(filename):
    return is_elf_file(filename)


def is_pcap(filename):
    pcap_magic = b"\xd4\xc3\xb2\xa1"
    with open(filename, "rb") as fh:
        length_to_read = len(pcap_magic)
        if fh.read(length_to_read) == pcap_magic:
            return True
    return False
