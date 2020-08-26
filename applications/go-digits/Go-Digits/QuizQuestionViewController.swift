/*
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
*/

import UIKit
import CoreML
import AVFoundation

extension CGImage {
    func invertedImage() -> CGImage? {
        let ciImage = CoreImage.CIImage(cgImage: self)
        guard let filter = CIFilter(name: "CIColorInvert") else { return nil }
        filter.setDefaults()
        filter.setValue(ciImage, forKey: kCIInputImageKey)
        let context = CIContext(options: nil)
        guard let outputImage = filter.outputImage else { return nil }
        guard let outputImageCopy = context.createCGImage(outputImage, from: outputImage.extent) else { return nil }
        return outputImageCopy
    }
}

class QuizQuestionViewController: UIViewController, AVSpeechSynthesizerDelegate {
    
    @IBOutlet weak var pageLabel: UILabel!
    @IBOutlet weak var quetionLabel: UILabel!
    var questionNumer = 0
    let numberOfQuestions = 10
    var numberToGuess = 0
    var score = 0.0
    @IBOutlet weak var goButton: UIButton!
    
    let synthesizer = AVSpeechSynthesizer()
    let syncSynthesizer = AVSpeechSynthesizer()
    
    @IBOutlet weak var drawView: DrawView!
    
    let model = mnistCNN()
    var inputImage: CGImage!
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if let results = segue.destination as? ResultsViewController {
            results.score = score/Double(numberOfQuestions)
        }
    }
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        questionNumer = questionNumer + 1
        
        if questionNumer >= numberOfQuestions {
            let vc = ResultsViewController()
            vc.score = score/Double(numberOfQuestions)
            self.performSegue(withIdentifier: "Finish", sender: self)
        } else {
            askQuestion()
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        syncSynthesizer.delegate = self
        score = 0.0
        askQuestion()
    }
    
    @IBAction func tappedClear(_ sender: Any) {
        drawView.lines = []
        drawView.setNeedsDisplay()
    }
    
    func askQuestion() {
        drawView.lines = []
        drawView.setNeedsDisplay()
        pageLabel.text = "\(questionNumer+1)/\(numberOfQuestions)"
        
        numberToGuess = Int(arc4random_uniform(8) + 1)
        
        let text = "Can you draw the number \(numberToGuess)?"
        let attrText = NSMutableAttributedString(string: text)
        attrText.setColorForText(String(numberToGuess), with: UIColor(red: 0.88, green: 0.1, blue: 0.88, alpha: 1.0))
        quetionLabel.attributedText = attrText
        
        let utterance = AVSpeechUtterance(string: text)
        utterance.rate = 0.4
        synthesizer.speak(utterance)
        
        drawView.isUserInteractionEnabled = true
        goButton.isEnabled = true
    }
    
    @IBAction func tappedDetect(_ sender: Any) {
        drawView.isUserInteractionEnabled = false
        goButton.isEnabled = false
        let context = drawView.getViewContext()
        inputImage = context?.makeImage()
        
        let invertedImage = inputImage.invertedImage()
        
        let pixelBuffer = UIImage(cgImage: invertedImage!).pixelBuffer()
        
        let output = try? model.prediction(input1: pixelBuffer!)
        let output1 = output!.output1
        var prob: Double = output1[0].doubleValue
        var digit:String = "0"
        
        for index in 0...output1.count-2 {
            if output1[index+1].doubleValue >= prob {
                prob = output1[index + 1].doubleValue
                digit = String(index+1)
            }
        }
        
        var feedback = ""
        let rightAnswerProb = output1[numberToGuess].doubleValue
        
        if Int(digit) == numberToGuess {
            if prob > 0.98 {
                feedback = "Excellent! You've written beautiful \(digit)!"
            } else if prob > 0.8 {
                feedback = "You did great. It's very nice \(digit)."
            }else if prob > 0.6 {
                feedback = "\(digit) can be recognized but probably you should work on your writting style."
            } else {
                feedback = "Your \(digit) is hard to recognize. You should do some practice."
            }
        } else {
            if prob > 0.8 {
                feedback = "It seems you've written \(digit) instead of \(numberToGuess)."
            } else {
                feedback = "Are you sure this is digit?"
            }
        }
        
        score = score + rightAnswerProb
        
        let utterance = AVSpeechUtterance(string: feedback)
        utterance.rate = 0.4
        syncSynthesizer.speak(utterance)
    }
    
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    
}

extension UIImage {
    func pixelBuffer() -> CVPixelBuffer? {
        let width = self.size.width
        let height = self.size.height
        let attrs = [kCVPixelBufferCGImageCompatibilityKey: kCFBooleanTrue,
                     kCVPixelBufferCGBitmapContextCompatibilityKey: kCFBooleanTrue] as CFDictionary
        var pixelBuffer: CVPixelBuffer?
        let status = CVPixelBufferCreate(kCFAllocatorDefault,
                                         Int(width),
                                         Int(height),
                                         kCVPixelFormatType_OneComponent8,
                                         attrs,
                                         &pixelBuffer)
        
        guard let resultPixelBuffer = pixelBuffer, status == kCVReturnSuccess else {
            return nil
        }
        
        CVPixelBufferLockBaseAddress(resultPixelBuffer, CVPixelBufferLockFlags(rawValue: 0))
        let pixelData = CVPixelBufferGetBaseAddress(resultPixelBuffer)
        
        let grayColorSpace = CGColorSpaceCreateDeviceGray()
        guard let context = CGContext(data: pixelData,
                                      width: Int(width),
                                      height: Int(height),
                                      bitsPerComponent: 8,
                                      bytesPerRow: CVPixelBufferGetBytesPerRow(resultPixelBuffer),
                                      space: grayColorSpace,
                                      bitmapInfo: CGImageAlphaInfo.none.rawValue) else {
                                        return nil
        }
        
        context.translateBy(x: 0, y: height)
        context.scaleBy(x: 1.0, y: -1.0)
        
        UIGraphicsPushContext(context)
        self.draw(in: CGRect(x: 0, y: 0, width: width, height: height))
        UIGraphicsPopContext()
        CVPixelBufferUnlockBaseAddress(resultPixelBuffer, CVPixelBufferLockFlags(rawValue: 0))
        
        return resultPixelBuffer
    }
}

