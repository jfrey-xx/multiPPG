import readerLSL

if __name__ == "__main__":
  reader = readerLSL.ReaderLSL("PPG")
  while True:
    reader()
