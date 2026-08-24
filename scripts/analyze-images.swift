#!/usr/bin/env swift

import AppKit
import Foundation
import Vision

guard CommandLine.arguments.count > 1 else {
  FileHandle.standardError.write(Data("Usage: analyze-images.swift <image>...\n".utf8))
  exit(2)
}

func rectDictionary(_ rect: CGRect) -> [String: Double] {
  [
    "x": rect.origin.x,
    "y": rect.origin.y,
    "width": rect.size.width,
    "height": rect.size.height
  ]
}

for input in CommandLine.arguments.dropFirst() {
  autoreleasepool {
    let path = URL(fileURLWithPath: input)
    guard
      let image = NSImage(contentsOf: path),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil)
    else {
      FileHandle.standardError.write(Data("Unable to read image: \(input)\n".utf8))
      exit(1)
    }

    let textRequest = VNRecognizeTextRequest()
    textRequest.recognitionLevel = .accurate
    textRequest.usesLanguageCorrection = true
    textRequest.recognitionLanguages = ["zh-Hans", "en-US"]

    let faceRequest = VNDetectFaceRectanglesRequest()
    let barcodeRequest = VNDetectBarcodesRequest()
    let handler = VNImageRequestHandler(cgImage: cgImage)

    do {
      try handler.perform([textRequest, faceRequest, barcodeRequest])
    } catch {
      FileHandle.standardError.write(Data("Vision analysis failed for \(input): \(error)\n".utf8))
      exit(1)
    }

    let texts: [[String: Any]] = (textRequest.results ?? []).compactMap { observation in
      guard let candidate = observation.topCandidates(1).first else {
        return nil
      }
      return [
        "text": candidate.string,
        "confidence": Double(candidate.confidence),
        "box": rectDictionary(observation.boundingBox)
      ]
    }

    let faces: [[String: Any]] = (faceRequest.results ?? []).map { observation in
      ["box": rectDictionary(observation.boundingBox)]
    }

    let barcodes: [[String: Any]] = (barcodeRequest.results ?? []).map { observation in
      [
        "symbology": String(describing: observation.symbology),
        "payload": observation.payloadStringValue ?? "",
        "box": rectDictionary(observation.boundingBox)
      ]
    }

    let result: [String: Any] = [
      "path": input,
      "width": cgImage.width,
      "height": cgImage.height,
      "texts": texts,
      "faces": faces,
      "barcodes": barcodes
    ]

    do {
      let data = try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys])
      print(String(decoding: data, as: UTF8.self))
    } catch {
      FileHandle.standardError.write(Data("Unable to encode analysis for \(input): \(error)\n".utf8))
      exit(1)
    }
  }
}
