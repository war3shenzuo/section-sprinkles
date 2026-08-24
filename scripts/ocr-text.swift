#!/usr/bin/env swift

import AppKit
import Foundation
import Vision

guard CommandLine.arguments.count > 1 else {
  FileHandle.standardError.write(Data("Usage: ocr-text.swift <image>...\n".utf8))
  exit(2)
}

for input in CommandLine.arguments.dropFirst() {
  let path = URL(fileURLWithPath: input)
  guard
    let image = NSImage(contentsOf: path),
    let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil)
  else {
    FileHandle.standardError.write(Data("Unable to read image: \(input)\n".utf8))
    exit(1)
  }

  let request = VNRecognizeTextRequest()
  request.recognitionLevel = .accurate
  request.usesLanguageCorrection = true
  request.recognitionLanguages = ["zh-Hans", "ja-JP", "en-US"]

  let handler = VNImageRequestHandler(cgImage: cgImage)
  do {
    try handler.perform([request])
  } catch {
    FileHandle.standardError.write(Data("OCR failed for \(input): \(error)\n".utf8))
    exit(1)
  }

  print("=== \(input) ===")
  for observation in request.results ?? [] {
    if let text = observation.topCandidates(1).first?.string {
      print(text)
    }
  }
}

