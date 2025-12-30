using System;
using System.IO;
using System.Linq;

// Folder to scan
var root = @"C:\xxxlutz\IG-Creator\XXXLutz\ICOM";

// Output file
var outputFile = "json_file_list.txt";

// Collect all JSON files recursively
var jsonFiles =
    Directory.GetFiles(root, "*.json", SearchOption.AllDirectories)
             .OrderBy(path => path)
             .ToList();

// Write to output file
File.WriteAllLines(outputFile, jsonFiles);

Console.WriteLine($"Found {jsonFiles.Count} JSON files.");
Console.WriteLine($"Written to: {Path.GetFullPath(outputFile)}");