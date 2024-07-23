#include "MainComponent.h"

//==============================================================================
MainComponent::MainComponent()
{
    setSize (700, 400);

    logScreenL.setMultiLine           (true);
    logScreenL.setScrollbarsShown     (false);
    logScreenL.setReadOnly            (true);
    logScreenL.setPopupMenuEnabled    (true);
    logScreenL.setTextToShowWhenEmpty ("LEFT HAND LOG SCREEN", juce::Colours::white);
    addAndMakeVisible                 (&logScreenL);

    logScreenR.setMultiLine           (true);
    logScreenR.setScrollbarsShown     (false);
    logScreenR.setReadOnly            (true);
    logScreenR.setPopupMenuEnabled    (true);
    logScreenR.setTextToShowWhenEmpty ("RIGHT HAND LOG SCREEN", juce::Colours::white);
    addAndMakeVisible                 (&logScreenR);

    if (! connect (7500))
        showConnectionErrorMessage ("Error: could not connect receiver to UDP port 7500");

    addListener (this, "/mediapipe/handsL");
    addListener (this, "/mediapipe/handsR");
    addListener (this, "/mediapipe/posL");
    addListener (this, "/mediapipe/posR");

    testSlider.setRange        (0.1, 100.0);
    testSlider.setSliderStyle  (juce::Slider::LinearHorizontal);
    testSlider.setTextBoxStyle (juce::Slider::TextBoxAbove, true, 150, 25);
    addAndMakeVisible (&testSlider);

    testCombo.setText ("Preset:");
    testCombo.addItem ("1", 1);
    testCombo.addItem ("2", 2);
    testCombo.addItem ("3", 3);
    testCombo.addItem ("4", 4);
    testCombo.addItem ("7", 7);
    testCombo.addItem ("10", 10);
    addAndMakeVisible (&testCombo);

    testCombo.onChange = [this]
        {
            if (! senderEC2.send ("/juce/preset", (float) testCombo.getSelectedId()))
                showConnectionErrorMessage ("Error: could not send OSC message to Emission Control 2");
        };

    testSlider.onValueChange = [this]
        {
            // create and send an OSC message with an address and a float value:
            if (! senderOR.send ("/juce/dry", (float) testSlider.getValue()))
                showConnectionErrorMessage ("Error: could not send OSC message to Emission Control 2");
        };

    if (! senderEC2.connect ("127.0.0.1", 7501))
        showConnectionErrorMessage ("Error: could not connect Emission Control 2 sender to UDP port 7501");

    if (! senderOR.connect ("127.0.0.1", 7502))
        showConnectionErrorMessage ("Error: could not connect Oril River sender to UDP port 7502");
}

MainComponent::~MainComponent()
{
    removeListener (this);
}

//==============================================================================
void MainComponent::paint (juce::Graphics& g)
{
    // (Our component is opaque, so we must completely fill the background with a solid colour)
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));
}

void MainComponent::resized()
{
    auto logScreenHeight = 340;

    auto area          = getLocalBounds();
    auto logScreenArea = area.removeFromBottom (logScreenHeight);

    logScreenL.setBounds (logScreenArea.removeFromLeft (
                          logScreenArea.getWidth() / 2)
                          .reduced(5));

    logScreenR.setBounds (logScreenArea.reduced (5));

    testCombo.setBounds (area.removeFromLeft (area.getWidth() / 2).reduced (10));

    testSlider.setBounds (area.reduced (10));
}

//===============================================================================
void MainComponent::oscMessageReceived (const juce::OSCMessage& message)
{
    /*if (message.size() != 5)
    {
        showArgumentErrorMessage ("Error: invalid size of message");
        return;
    }*/

    /*for (auto arg : message)
        if (! arg.isInt32())
        {
            showArgumentErrorMessage ("Error: some argument is not Int32");
            return;
        }*/
    
    /*logMessage (" - Received OSC message with address "
                + message.getAddressPattern().toString()
                + " with "
                + juce::String (message.size())
                + " argument(s):", 0);*/

    if (message.getAddressPattern() == "/mediapipe/handsL")
    {
        leftHand.gesture = message[0].getInt32();
        leftHand.numeric = message[1].getInt32();
    }
    else if (message.getAddressPattern() == "/mediapipe/handsR")
    {
        rightHand.gesture = message[0].getInt32();
        rightHand.numeric = message[1].getInt32();
    }
    else if (message.getAddressPattern() == "/mediapipe/posL")
    {
        leftHand.x = message[0].getInt32();
        leftHand.y = message[1].getInt32();
    }
    else if (message.getAddressPattern() == "/mediapipe/posR")
    {
        rightHand.x = message[0].getInt32();
        rightHand.y = message[1].getInt32();
    }
    
    logScreenL.clear();
    logScreenR.clear();

    logMessage (" -- Gesture -> "         + juce::String (leftHand.gesture), 0);
    logMessage (" -- Hand -> 0", 0);
    logMessage (" -- X position -> "      + juce::String (leftHand.x), 0);
    logMessage (" -- Y position -> "      + juce::String (leftHand.y), 0);
    logMessage (" -- Numeric gesture -> " + juce::String (leftHand.numeric), 0);

    logMessage (" -- Gesture -> "         + juce::String (rightHand.gesture), 1);
    logMessage (" -- Hand -> 1", 1);
    logMessage (" -- X position -> "      + juce::String (rightHand.x), 1);
    logMessage (" -- Y position -> "      + juce::String (rightHand.y), 1);
    logMessage (" -- Numeric gesture -> " + juce::String (rightHand.numeric), 1);

    //switch (message[1].getInt32())
    //{
    //case 0: // Update left hand
    //    leftHand.gesture = message[0].getInt32();
    //    leftHand.x       = message[2].getInt32();
    //    leftHand.y       = message[3].getInt32();
    //    leftHand.numeric = message[4].getInt32();

    //    logScreenL.clear();

    //    logMessage (" -- Gesture -> "         + juce::String (message[0].getInt32()), 0);
    //    logMessage (" -- Hand -> "            + juce::String (message[1].getInt32()), 0);
    //    logMessage (" -- X position -> "      + juce::String (message[2].getInt32()), 0);
    //    logMessage (" -- Y position -> "      + juce::String (message[3].getInt32()), 0);
    //    logMessage (" -- Numeric gesture -> " + juce::String (message[4].getInt32()), 0);

    //    /*updateHands (leftHand_old,
    //                 message[0].getInt32(),
    //                 message[1].getInt32(),
    //                 message[2].getInt32(),
    //                 message[3].getInt32(),
    //                 message[4].getInt32());*/
    //    break;

    //case 1: // Update right hand
    //    rightHand.gesture = message[0].getInt32();
    //    rightHand.x       = message[2].getInt32();
    //    rightHand.y       = message[3].getInt32();
    //    rightHand.numeric = message[4].getInt32();
    //    
    //    logScreenL.clear();

    //    logMessage (" -- Gesture -> "         + juce::String (message[0].getInt32()), 1);
    //    logMessage (" -- Hand -> "            + juce::String (message[1].getInt32()), 1);
    //    logMessage (" -- X position -> "      + juce::String (message[2].getInt32()), 1);
    //    logMessage (" -- Y position -> "      + juce::String (message[3].getInt32()), 1);
    //    logMessage (" -- Numeric gesture -> " + juce::String (message[4].getInt32()), 1);
    //    
    //    /*updateHands (rightHand_old,
    //                 message[0].getInt32(),
    //                 message[1].getInt32(),
    //                 message[2].getInt32(),
    //                 message[3].getInt32(),
    //                 message[4].getInt32());*/
    //    break;

    //default: // Error
    //    showArgumentErrorMessage ("Error: do you have three hands???");
    //    return;
    //}

    juce::String error = "";
    if (! resend (error)) showConnectionErrorMessage (error);

    /*for (juce::OSCArgument arg : message)
        logMessage (OSCArgToString (arg));*/

}

void MainComponent::showConnectionErrorMessage (const juce::String& message)
{
    juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                            "Connection error",
                                            message,
                                            "OK");
}

void MainComponent::showArgumentErrorMessage (const juce::String& message)
{
    juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                            "Argument error",
                                            message,
                                            "OK");
}

void MainComponent::logMessage (const juce::String& m, int hand)
{
    switch (hand)
    {
    case 0:
        logScreenL.moveCaretToEnd();
        logScreenL.insertTextAtCaret (m + juce::newLine);
        break;
    case 1:
        logScreenR.moveCaretToEnd();
        logScreenR.insertTextAtCaret (m + juce::newLine);
        break;
    default: break;
    }
}

//==============================================================================
void MainComponent::handleConnectError (int failedPort)
{
    juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                            "OSC Connection error",
                                            "Error: could not connect to port " + juce::String (failedPort),
                                            "OK");
}

void MainComponent::handleDisconnectError()
{
    juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                            "Unknown error",
                                            "An unknown error occured while trying to disconnect from UDP port.",
                                            "OK");
}

void MainComponent::handleInvalidPortNumberEntered()
{
    juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                            "Invalid port number",
                                            "Error: you have entered an invalid UDP port number.",
                                            "OK");
}

//=============================================================================
/**
 DEPRECATED
*/
void MainComponent::updateHands (handParams_old& params, int gest, int hand, int x, int y, int num)
{
            // Repetition check for gesture
            if (gest == params.newGesture) params.timesSeenGest++;
            else                           params.timesSeenGest = 0;

            params.newGesture = gest;

            /*if (params.timesSeenGest == 10)*/ params.currentGesture = params.newGesture;

            // Repetition check for numeric gesture
            if (num == params.newNumeric) params.timesSeenNum++;
            else                          params.timesSeenNum = 0;

            params.newNumeric = num;

            /*if (params.timesSeenNum == 10)*/ params.currentNumeric = params.newNumeric;

            // X and Y
            params.x = x;
            params.y = y;
}

bool MainComponent::resend (juce::String& e)
{
    if (! senderEC2.send ("/juce/preset", (float) leftHand.numeric))
    {
        e = "Error: could not send preset to Emission Control 2";
        return false;
    }
    
    if (! senderEC2.send ("/juce/filterfreq", (float) rightHand.x))
    {
        e = "Error: could not send filter frequency to Emission Control 2";
        return false;
    }

    if (! senderEC2.send ("/juce/filterq", (float) rightHand.y))
    {
        e = "Error: could not send filter Q to Emission Control 2";
        return false;
    }

    /*if (!senderOR.send ("/juce/dry", (float) leftHand.y))
    {
        e = "Error: could not send dry to Oril River";
        return false;
    }*/

    return true;
}

/**
    * Deprecated/Unused |
    *
    * Translates an OSCArgument to its type and value.
    * For example, 0.835 will be shown as "Float32 -> 0.835"
    *
    * @param arg : A single argument from a juce::OSCMessage object
    * @return Translation of the given argument
    */
juce::String MainComponent::OSCArgToString (const juce::OSCArgument& arg)
{
    if      (arg.isFloat32()) return "Float32 -> " + juce::String (arg.getFloat32());
    else if (arg.isInt32())   return "Int32 -> "   + juce::String (arg.getInt32());
    else if (arg.isString())  return "String -> "  + juce::String (arg.getString());
    else if (arg.isColour())  return "Colour -> "  + juce::String (arg.getColour().toInt32());
    else if (arg.isBlob())    return "Blob -> "    + arg.getBlob().toString();
    else                      return "Unknown argument";
}