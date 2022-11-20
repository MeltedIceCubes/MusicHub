import pulsectl, time
pulse = pulsectl.Pulse('my-client-name')

# audio_source = source_list[2]

# volume = audio_source.volume
# print(volume.values)  # list of per-channel values (floats)
# print(volume.value_flat)  # average level across channels (float)

# volume.value_flat = 0.4  # sets all volume.values to 0.3
# pulse.volume_set(audio_source, volume)  # applies the change

# print("hihi")

#Music Hub 1 : F0_6E_0B_D3_BA_44
#Music Hub 2 : 98_52_3D_3E_97_DD
#Music Hub 3 : F4_65_A6_E5_F0_5F
Hubs = []

class PulseObj:
    def __init__(self, mac):
        self.SourceObj = None
        self.SinkObj   = None
        self.ControlObj= None
        self.Mac    = mac
        self.Peak = 0
    def MatchAddr(self, addr):
        if self.Mac in  addr:
            print(addr)
            return True
        else:
            pass
            # print("no match")
        return False
    def CheckControl(self):
        """
        If this object has both source and sink, it means it's a speaker.
        If it's a speaker, it will have to be controller on the sink Obj
        """
        # Sink Case
        if (self.SourceObj is not None) and (self.SinkObj is not None):
            self.ControlObj = self.SinkObj
        elif self.SourceObj is not None:  # Source Case
            self.ControlObj = self.SourceObj
        else:  # Dud case
            pass
    def SetVolume(self, vol_new):
        if self.ControlObj is not None:
            vol =  self.ControlObj.volume
            vol.value_flat = vol_new
            pulse.volume_set(self.ControlObj,vol)
        else:
            return None
    def GetPeak(self):
        """https://github.com/mk-fg/python-pulse-control/blob/master/pulsectl/pulsectl.py"""
        # pulse.get_peak_sample(pulse.sink_info(si.sink).monitor_source, 0.8, si.index)
        self.Peak = pulse.get_peak_sample(self.SourceObj.name, 0.01)
        self.Print_Meter()
        # print(peak)
    def Print_Meter(self):
        print((" "*30), end = '\r')
        print(("*" * int(self.Peak*30)), end = '\r')
        time.sleep(0.01)





def Get_SrcSink():
    global pulse, Hubs
    source_list = pulse.source_list()
    sink_list = pulse.sink_list()
    for Hub in Hubs:
        # print("Starting Scan for %s" %Hub.Mac)
        # print("Finding sources")
        for source in source_list:
            if Hub.MatchAddr(source.name):
                Hub.SourceObj = source
        # print("Finding Sinks")
        for sink in sink_list:
            if Hub.MatchAddr(sink.name):
                Hub.SinkObj = sink
        Hub.CheckControl()


def main():
    global Hubs
    Hubs.append(PulseObj("F0_6E_0B_D3_BA_44"))
    Hubs.append(PulseObj("98_52_3D_3E_97_DD"))
    Hubs.append(PulseObj("F4_65_A6_E5_F0_5F"))
    Get_SrcSink()
    # while True:
    #     x = input()
    #     Hubs[1].SetVolume(float(x))
    while True:
        Hubs[1].GetPeak()
    print("Done")

if __name__ == "__main__":
    main()