# BRANCH MASTER: source Web app

## Run locally
Download Pycharm: https://www.jetbrains.com/pycharm/

Open source code in PyCharm and install dependencies in `requirement.txt`

Link demo: https://www.youtube.com/watch?v=FHdRpVvyZeU&feature=youtu.be

## Run website
Link web app: https://secret-shelf-15633.herokuapp.com/

Demo web app on server: https://youtu.be/2iKH2VK1DEA


# BRANCH lacDa: source Algorithms
## LOSSY JPEG
We provide JPEG-ENCODER (Lossy Compression Algorithms) combine with Lossless Compression Algorithms (Huffman, LZW, ARITHMETIC).

## Run Code: 
```sh
$ cd Lossy_JPEG
$ python run.py [-h] -i INPUT [-f FLAG] [-m METHOD]
```
- -i INPUT: Path Image
- -f FlAG : Choose: 0 :Compress | 1 :Decompress (default : 0)
- -m METHOD: Choose method: 0 :JPEG encoder with Huffman Coding | 1 :JPEG encoder LZW Coding | 2 :JPEG encoder Arithmetic Coding | 3 :LZW Lossless Coding (default: 0)
- Note:
    - Input images are saved in `input` folder.
    - Compressed file are saved in `compressed_file` folder.
    - Restored images are saved in `restored_images` folder.
