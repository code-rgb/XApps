# Apk Downloader

Uses github action to fetch and download latest apk from `config.yaml` and then packs it into `pakages.tar.gz` that can be easily extracted and installed via root or ADB

## Supports Downloading from:

- Github releases
- F-Droid
- PlayStore
- Json based API
- Misc. (see config.yaml for more info)

## Usage

1. Fork And Edit config.yaml
2. Start Github Action Manually

## Apk Install Command

Extract tarball to folder `pakages`

```bash
tar -xvf pakages.tar.gz && rm pakages.tar.gz
```

### Termux

**Note:** Use Latest [Termux from F-Droid](https://f-droid.org/en/packages/com.termux/)

- Root
```bash
for app in pakages/*.apk; do
  pm install $app
done
```

- Non-root
```bash
for app in pakages/*.apk; do
  termux-open install $app
  sleep(8)
done
```

### ADB

Go to ADB folder, connect your phone and run the below commands in the terminal

> Powershell

```powershell
Get-ChildItem "pakages/" -Filter *.apk | 
Foreach-Object {
    adb install -r $_.FullName
}
```

> Bash

```bash
for app in pakages/*.apk; do
  adb install -r $app
done
```
