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

extension NSMutableAttributedString{
    func setColorForText(_ textToFind: String, with color: UIColor) {
        let range = self.mutableString.range(of: textToFind, options: .caseInsensitive)
        self.addAttribute(NSAttributedStringKey.foregroundColor, value: color , range: range)
    }
}
