#!/usr/bin/python3
#coding: utf-8
#
# version revisited 0002 (30/09/21) by RickalineD634 ;)
# Requirements:
# - Space disk you set into args or the default amount value (default 30G)
# - Suffisent RAM Disk because the blocsize of an call to `dd` command is setted to 1G
# - An Arch Linux Based for Operating System
# - Firewall settings to allow pacman usage
# - Network connection to internet
# - Compatibility with python3.9
import argparse
from os import system
parser = argparse.ArgumentParser("script-setup-luks-on-home v1 - By Rick Sanchez D-634 (AKA 0x07CB)")
parser.add_argument("image", type=str,
        help="Image file name.")
parser.add_argument("-s","--size-disk", type=int,
        help="Set disk size (in Gig).[default: 30]")
parser.add_argument("--key-size", type=int,
        help="Set key size used for the encryption(Algorithm used is AES in XTS-plain64 mode).[default: 512]")
parser.add_argument("--priv-key-size", type=int,
        help="Set private key size(replacement of passphrase to open luks-encrypted disk).[default: 8912]")
parser.add_argument("--install-deps", action="store_true",
        help="install dependences packages before setup.")
#defaults
size_disk_G, key_size, priv_key_size = 30, 512, 8912

#dossier de l'image chifree 
src_dir_img = "/vdisks/crypto/"
system("mkdir -p {src_dir_img}".format(
        src_dir_img = src_dir_img
      ))

#parsing
args = parser.parse_args()
if args.size_disk:
    size_disk_G = args.size_disk
if args.key_size:
    key_size = args.key_size
if args.priv_key_size:
    priv_key_size = args.priv_key_size
img_filename = args.image

SCRIPT_INSTALL_DEPS_PACKAGES = """
sudo pacman -Syu
sudo pacman -S cryptsetup wipe python3 openssl rsync
"""

if args.install_deps:
    system(SCRIPT_INSTALL_DEPS_PACKAGES)

SCRIPT_CREATE_DISK_LUKS_IMG = """
sudo dd if=/dev/zero of={src_dir_img}{image_filename}.img bs=1G count={size_disk_G} iflag=fullblock status=progress
sudo openssl genrsa -out {image_filename}.priv {priv_key_size}
sudo cryptsetup luksFormat --cipher aes-xts-plain64 --key-size {key_size} --key-file {image_filename}.priv --hash sha512 --iter-time 7000 {src_dir_img}{image_filename}.img
sudo cryptsetup luksOpen --key-file {image_filename}.priv {src_dir_img}{image_filename}.img crypt-home
sudo mkfs.ext4 /dev/mapper/crypt-home
sudo mkdir -p /mnt/crypt-home
sudo mount /dev/mapper/crypt-home /mnt/crypt-home
""".format(
    image_filename = img_filename,
    src_dir_img = src_dir_img,
    size_disk_G = size_disk_G,
    key_size = key_size,
    priv_key_size = priv_key_size
)

system(SCRIPT_CREATE_DISK_LUKS_IMG)

# APPEND INSERT THE CRYPTTAB AND FSTAB CONFIG TO AUTOMOUNT
CONFIG_LINE_CRYPTTAB = "\n{}\n".format("\ncrypt-home          {src_dir_img}{image_filename}.img        {image_filename}.priv\n".format(
        image_filename = img_filename,
        src_dir_img = src_dir_img
))

CONFIG_LINE_FSTAB = "\n{}\n".format("\n/dev/mapper/crypt-home          /mnt/crypt-home         ext4        defaults        0 2\n")

system("chown -R root:root {src_dir_img}".format(
        src_dir_img = src_dir_img
      ))

with open("/etc/crypttab", 'a') as f:
    f.write(CONFIG_LINE_CRYPTTAB)
    f.close()

with open("/etc/fstab", 'a') as f:
    f.write(CONFIG_LINE_FSTAB)
    f.close()

SCRIPT_SETUP_HOME_TO_ENCRYPTED = """
sudo rsync -arpP /home /mnt/crypt-home/
sudo rm -rf /home
sudo ln -s /mnt/crypt-home/home /home
"""

system(SCRIPT_SETUP_HOME_TO_ENCRYPTED)
