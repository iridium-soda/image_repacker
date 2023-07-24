# image_repacker
A tool to repack modified image files automatically.

This repo fix the modified image's digest automatically and tar it. A simple script to help me push broken images to Dockerhub.

## How docker image organized 

After exporting an image by `docker save` and `tar -xvf`, the dir shows the following structure:

```plaintext
.
├── 81f3f27e365c8ae00dc6534173bd5cea0fde798b82785203475515970649c588.json
├── 83cb78f77b90249ffac6eee25f37091931addccb562cb11d264671ad7a749dc0
│   ├── json
│   ├── layer.tar
│   └── VERSION
├── c0d586f9f3f1373585e86cd27a38c2f434088954e5617bf474f780d4eeb3c4c2
│   ├── json
│   ├── layer.tar
│   └── VERSION
├── manifest.json
└── repositories

2 directories, 9 files
```

- `81...`:该文件的sha256,也是该镜像的id(digest)
- `81f3f27e365c8ae00dc6534173bd5cea0fde798b82785203475515970649c588.json:rootfs`
    - `diff_ids`: 目录下`layer.tar`的sha256
- `manifest.json`:
    - `Config`：81...
    - `Layers`：`layer.tar`的目录 应该不用改
- `c0d5...`:这个id似乎可以不用管，可以乱写


## Reference

- https://hstar.me/2020/09/cve-2018-8115-analysis
- https://docs.docker.com/registry/spec/manifest-v2-2/#image-manifest-field-descriptions