# Object-oriented file system

![Actions Status](https://github.com/darwinz/oo-file-system/workflows/GitHub%20Actions/badge.svg)

An object-oriented file-system developed in Python

### File system design

Types of file system entities
* Drive
* Folder
* Text File
* Zip File

These entities obey the following relations:
* A folder, a drive or a zip file, may contain zero to many other folders, or files (text or zip)
* A text file does not contain any other entity
* A drive is not contained in any entity
* Any non-drive entity must be contained in another entity

If entity A contains entity B then we say that A is the parent of B

Every entity has the following properties:
* Type – The type of the entity (one of the 4 types above)
* Name - An alphanumeric string. Two entities with the same parent cannot have the same name. Similarly, two drives cannot have the same name
* Path – The concatenation of the names of the containing entities, from the drive down to and including the entity
* A text file has a property called Content which is a string
* Size – an integer defined as follows:
    * For a text file – it is the length of its content
    * For a drive or a folder, it is the sum of all sizes of the entities it contains
    * For a zip file, it is one half of the sum of all sizes of the entities it contains

The system is capable of supporting the following file-system-like operations:
1. Create – Creates a new entity
2. Delete – Deletes an existing entity (and all the entities it contains)
3. Move – Changing the parent of an entity
4. WriteToFile – Changes the content of a text file

### End User module

An "end-user" module can be used to interact with the system.  With it,
you can create folders, text files, etc. and write to files, along
with checking the size of folders and files in the file system

### Testing

You can run unit tests by running the following command

```shell
python -m unittest tests/test_*
```
