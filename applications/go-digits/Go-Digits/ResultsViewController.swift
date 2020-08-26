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

class ResultsViewController: UIViewController, AVSpeechSynthesizerDelegate {
    @IBOutlet weak var feedbackTitle: UILabel!
    @IBOutlet weak var feedbackBg: UIImageView!
    @IBOutlet weak var scoreLabel: UILabel!
    
    var score = 0.0
    
    let syncSynthesizer = AVSpeechSynthesizer()
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
    }
    
    func prepareResult() {
        score = score.squareRoot().squareRoot()
        let counted_score = Int(score*100)
        var title = ""
        
        if score > 0.9 {
            title = "Excellent!"
        } else if score > 0.8 {
            title = "Great!"
        } else if score > 0.7 {
            title = "Good!"
        } else if score > 0.6 {
            title = "OK"
        } else {
            title = "Try again"
        }
        
        feedbackTitle.text? = title
        
        let text = "Your score: \(counted_score)%"
        let attrText = NSMutableAttributedString(string: text)
        attrText.setColorForText("\(counted_score)%", with: UIColor(red: 0.88, green: 0.1, blue: 0.88, alpha: 1.0))
        self.scoreLabel.attributedText = attrText
        
        let utterance = AVSpeechUtterance(string: title)
        utterance.rate = 0.4
        syncSynthesizer.speak(utterance)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        syncSynthesizer.delegate = self
        prepareResult()
    }
}
