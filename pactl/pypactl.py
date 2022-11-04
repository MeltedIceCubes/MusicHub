import pulsectl
pulse = pulsectl.Pulse('my-client-name')
source_list = pulse.source_list()
sink_list = pulse.sink_list()
audio_source = source_list[2]
volume = audio_source.volume
print(volume.values)  # list of per-channel values (floats)
print(volume.value_flat)  # average level across channels (float)

volume.value_flat = 0.4  # sets all volume.values to 0.3
pulse.volume_set(audio_source, volume)  # applies the change

print("hihi")
