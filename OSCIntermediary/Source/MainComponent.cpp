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

    if (! senderEC2.connect ("127.0.0.1", 7501))
        showConnectionErrorMessage ("Error: could not connect Emission Control 2 sender to UDP port 7501");

    testSlider.onValueChange = [this]
        {
            // create and send an OSC message with an address and a float value:
            if (!senderEC2.send ("/juce/test", (float) testSlider.getValue()))
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

    testSlider.setBounds (area.reduced (10));
}

//===============================================================================
void MainComponent::oscMessageReceived (const juce::OSCMessage& message)
{
    logMessage("mensaje recibido");

    logMessage (" - Received OSC message with address "
                + message.getAddressPattern().toString()
                + " with "
                + juce::String (message.size())
                + " argument(s):");

    for (juce::OSCArgument arg : message)
        logMessage (OSCArgToString (arg));
}

void MainComponent::showConnectionErrorMessage (const juce::String& message)
{
    juce::AlertWindow::showMessageBoxAsync (juce::AlertWindow::WarningIcon,
                                            "Connection error",
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
juce::String MainComponent::OSCArgToString (const juce::OSCArgument& arg)
{
    if      (arg.isFloat32()) return "Float32 -> " + juce::String (arg.getFloat32());
    else if (arg.isInt32())   return "Int32 -> "   + juce::String (arg.getInt32());
    else if (arg.isString())  return "String -> "  + juce::String (arg.getString());
    else if (arg.isColour())  return "Colour -> "  + juce::String (arg.getColour().toInt32());
    else if (arg.isBlob())    return "Blob -> "    + arg.getBlob().toString();
    else                      return "Unknown argument";
}