#include "MainComponent.h"

//==============================================================================
MainComponent::MainComponent()
{
    setSize (700, 400);

    logScreen.setMultiLine        (true);
    logScreen.setScrollbarsShown  (false);
    logScreen.setReadOnly         (true);
    logScreen.setPopupMenuEnabled (true);
    addAndMakeVisible             (&logScreen);

    if (! connect (7500))
        showConnectionErrorMessage ("Error: could not connect receiver to UDP port 7500");

    addListener (this, "/mediapipe/hands");

    testSlider.setRange (0.1, 100.0);
    testSlider.setSliderStyle (juce::Slider::LinearHorizontal);
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

    if (! senderEC2.connect ("127.0.0.1", 7501))
        showConnectionErrorMessage ("Error: could not connect Emission Control 2 sender to UDP port 7501");

    testSlider.onValueChange = [this]
        {
            // create and send an OSC message with an address and a float value:
            if (! senderEC2.send ("/juce/grainrate", (float) testSlider.getValue()))
                showConnectionErrorMessage ("Error: could not send OSC message to Emission Control 2");
        };
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

    logScreen.setBounds (logScreenArea.reduced (5));

    testCombo.setBounds (area.removeFromLeft (area.getWidth() / 2).reduced (10));

    testSlider.setBounds (area.reduced (10));
}

//===============================================================================
void MainComponent::oscMessageReceived (const juce::OSCMessage& message)
{
    if (message.size() != 5)
    {
        showArgumentErrorMessage ("Error: invalid size of message");
        return;
    }

    for (auto arg : message)
        if (! arg.isInt32())
        {
            showArgumentErrorMessage ("Error: some argument is not Int32");
            return;
        }
    
    /*logMessage (" - Received OSC message with address "
                + message.getAddressPattern().toString()
                + " with "
                + juce::String (message.size())
                + " argument(s):");*/

    logScreen.clear();

    logMessage (" -- Gesture -> "         + juce::String (message[0].getInt32()));
    logMessage (" -- Hand -> "            + juce::String (message[1].getInt32()));
    logMessage (" -- X position -> "      + juce::String (message[2].getInt32()));
    logMessage (" -- Y position -> "      + juce::String (message[3].getInt32()));
    logMessage (" -- Numeric gesture -> " + juce::String (message[4].getInt32()));
    
    switch (message[1].getInt32())
    {
    case 0: // Update left hand
        updateHands (leftHand,
                     message[0].getInt32(),
                     message[1].getInt32(),
                     message[2].getInt32(),
                     message[3].getInt32(),
                     message[4].getInt32());
        break;

    case 1: // Update right hand
        updateHands (rightHand,
                     message[0].getInt32(),
                     message[1].getInt32(),
                     message[2].getInt32(),
                     message[3].getInt32(),
                     message[4].getInt32());
        break;

    default: // Error
        showArgumentErrorMessage ("Error: do you have three hands???");
        return;
    }

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

void MainComponent::logMessage (const juce::String& m)
{
    logScreen.moveCaretToEnd();
    logScreen.insertTextAtCaret (m + juce::newLine);
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
void MainComponent::updateHands (handParams& params, int gest, int hand, int x, int y, int num)
{
            // Repetition check for gesture
            if (gest == params.newGesture) params.timesSeenGest++;
            else                           params.timesSeenGest = 0;

            params.newGesture = gest;

            if (params.timesSeenGest == 10) params.currentGesture = params.newGesture;

            // Repetition check for numeric gesture
            if (num == params.newNumeric) params.timesSeenNum++;
            else                          params.timesSeenNum = 0;

            params.newNumeric = num;

            if (params.timesSeenNum == 10) params.currentNumeric = params.newNumeric;

            // X and Y
            params.x = x;
            params.y = y;
}

bool MainComponent::resend (juce::String& e)
{
    if (! senderEC2.send ("/juce/preset", (float) leftHand.currentNumeric))
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