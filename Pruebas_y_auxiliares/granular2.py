#%%

from pyo import *
#print(getVersion())
port = 57120

#%%

s = Server(audio="portaudio",midi="portmidi")
# s = Server(audio="jack")
#s = Server()
s.boot()


#%%
#snd = SndTable("../snds/baseballmajeur_m.aif")
#file = '/home/jaime/repo/svn_jaime/docencia/music/supercollider/handsDronning/ambulation-main/droning/55hz_spacedrone.wav'
#file = 'erhu.wav'
#file = 'Guitar 1.wav'
file = 'guitarra-afinar-cuerda-uno-.wav'

snd = SndTable(file)

#snd.view()

# Remove sr/4 samples to the size of the table, just to be sure
# that the reading pointer never exceeds the end of the table.
# end = snd.getSize()[0] - s.getSamplingRate() * 0.25
end = snd.getSize() - s.getSamplingRate() * 0.25



# A Tuckey envelope for the grains (also known as flat-top envelope).
env = WinTable(7)
env.view(title="Grain envelope")

#env2 = HannTable(18)
#env2.view(title="han")


# The grain pitch has a default value of 1, to which we can add a
# randomness factor by raising the "mul" value of the Noise.
#pit = Noise(0, add=1)
#pit.ctrl([SLMap(0, 1, "lin", "mul", 0)], title="Pitch Randomness")


# The grain position oscillates slowly between the beginning and
# the end of the table. We add a little jitter to the position to
# attenuate phasing artifacts when overlapping the grains.
#pososc = Sine(0.05).range(0, end)
#posrnd = Noise(mul=0.01, add=1)
#pos = pososc * posrnd


pososc = Sine(0.05).range(0, end)
posrnd = Noise(mul=0.01, add=1)
pos = pososc * posrnd




pososc.ctrl()


gmul = 0.5 
gdens = 10.0
gdur = 0.1

gffr =1000.0
gfq = 1.0
gsplit = 1.0



# The grain panoramisation 
pan = Sine(freq=2, mul=.5)

grain = Particle2(
    table=snd,  # The table to read.
    env=env,  # The grain envelope.
    dens=gdens,  # The density of grains per second.
    # The next arguments are sampled at the beginning of the grain
    # and hold their until the end of the grain.
    #pitch=pit,  # The pitch of the grain.
    pitch=1.5,
    pos=pos,  # The position of the grain in the table.
    dur=gdur,  # The duration of the grain in seconds.
    dev=0.005,  # The maximum deviation of the start time,
    # synchronous versus asynchronous granulation.
    pan=pan,  # The pan value of the grain.
    filterfreq=gffr,  # The filter frequency of the grain.
    filterq=gfq,  # The filter Q of the grain.
    filtertype=3,  # The filter type of the grain.
    # End of sampled arguments.
    chnls=2,  # The output number of streams of the granulator.
    mul=gmul,
)
grain.ctrl()

# Some grains can be surprisingly loud so we compress the output of the granulator.
comp = Compress(grain, thresh=-20, ratio=4, risetime=0.005, falltime=0.10, knee=0.5, mul=2)


lfos = Sine(freq=[.3,.4,.5,.6,.7,.8], mul=.5, add=.5)
sig = BandSplit(comp, num=6, min=250, max=4000, q=5, mul=lfos)
sig.ctrl()

d = WGVerb(sig, feedback=[.74,.75], cutoff=5000, bal=.25, mul=.3).out()
d.ctrl()







#########################
## OSC
#########################


frScale = Map(50., 18000., 'log')
frQScale = Map(0.25, 100., 'log')
qScale = Map(0.100, 100., 'log')


# Function called whenever OscDataReceive receives an input.
def processOSCmessage(address, *args):  
    global gdens, gdur, gmul, gsplit
    global gffr, gfq
    print(args)  
    if address=='/left':  
        gdur = args[0] 
        gmul = args[1]
        gdens = args[2]*250      
        
        
    elif address=='/right':                
        gffr = frScale.get(args[0])
        gsplit = qScale.get(args[1])
        gfq = frQScale.get(args[2])

scan = OscDataReceive(port=port, address="*", function=processOSCmessage)



def update():
    grain.mul = gmul
    grain.dens = gdens    
    grain.dur = gdur
    grain.filterfreq = gffr
    grain.filterq = gfq
    sig.q = gsplit
    print(f'Mul {grain.mul:.2f}  Dur {grain.dur:.2f}  Dens {grain.dens:.2f}   Freq {grain.filterfreq:.2f}  Q {grain.filterq:.2f}  split {sig.q:.2f}')
   

pat2 = Pattern(function=update, time=0.2).play()







s.gui(locals())

