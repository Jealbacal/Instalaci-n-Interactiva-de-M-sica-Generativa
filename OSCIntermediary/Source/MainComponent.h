#pragma once

#include <JuceHeader.h>

//==============================================================================
/*
    This component lives inside our window, and this is where you should put all
    your controls and content.
*/
class MainComponent  : public juce::Component,
                       private juce::OSCReceiver,
                       private juce::OSCReceiver::ListenerWithOSCAddress<juce::OSCReceiver::MessageLoopCallback>
{
public:
    //==============================================================================
    MainComponent();
    ~MainComponent() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

private:
    //==============================================================================
    int currentPortNumber = -1;

    juce::TextEditor logScreen;

    juce::Slider testSlider;

    juce::OSCSender senderEC2; // The sender for EmissionControl2

    void oscMessageReceived         (const juce::OSCMessage& message) override;
    void showConnectionErrorMessage (const juce::String& message);
    void logMessage                 (const juce::String& m);

    //==============================================================================
    void handleConnectError (int failedPort);
    void handleDisconnectError();
    void handleInvalidPortNumberEntered();

    juce::String OSCArgToString (const juce::OSCArgument& arg);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainComponent)
};
