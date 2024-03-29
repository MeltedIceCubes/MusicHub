libpulsecommon_sources = [
  'pulse/client-conf.c',
  'pulse/error.c',
  'pulse/fork-detect.c',
  'pulse/format.c',
  'pulse/mainloop-api.c',
  'pulse/xmalloc.c',
  'pulse/proplist.c',
  'pulse/utf8.c',
  'pulse/channelmap.c',
  'pulse/sample.c',
  'pulse/util.c',
  'pulse/timeval.c',
  'pulse/rtclock.c',
  'pulse/volume.c',
  'pulsecore/authkey.c',
  'pulsecore/conf-parser.c',
  'pulsecore/core-error.c',
  'pulsecore/core-format.c',
  'pulsecore/core-rtclock.c',
  'pulsecore/core-util.c',
  'pulsecore/dynarray.c',
  'pulsecore/fdsem.c',
  'pulsecore/flist.c',
  'pulsecore/g711.c',
  'pulsecore/hashmap.c',
  'pulsecore/i18n.c',
  'pulsecore/idxset.c',
  'pulsecore/arpa-inet.c',
  'pulsecore/iochannel.c',
  'pulsecore/ioline.c',
  'pulsecore/ipacl.c',
  'pulsecore/json.c',
  'pulsecore/lock-autospawn.c',
  'pulsecore/log.c',
  'pulsecore/ratelimit.c',
  'pulsecore/mcalign.c',
  'pulsecore/memblock.c',
  'pulsecore/memblockq.c',
  'pulsecore/memchunk.c',
  'pulsecore/native-common.c',
  'pulsecore/once.c',
  'pulsecore/packet.c',
  'pulsecore/parseaddr.c',
  'pulsecore/pdispatch.c',
  'pulsecore/pid.c',
  'pulsecore/pipe.c',
  'pulsecore/memtrap.c',
  'pulsecore/aupdate.c',
  'pulsecore/proplist-util.c',
  'pulsecore/pstream-util.c',
  'pulsecore/pstream.c',
  'pulsecore/queue.c',
  'pulsecore/random.c',
  'pulsecore/srbchannel.c',
  'pulsecore/sample-util.c',
  'pulsecore/shm.c',
  'pulsecore/bitset.c',
  'pulsecore/socket-client.c',
  'pulsecore/socket-util.c',
  'pulsecore/strbuf.c',
  'pulsecore/strlist.c',
  'pulsecore/tagstruct.c',
  'pulsecore/time-smoother.c',
  'pulsecore/time-smoother_2.c',
  'pulsecore/tokenizer.c',
  'pulsecore/usergroup.c',
  'pulsecore/sndfile-util.c',
]

libpulsecommon_headers = [
  'pulse/client-conf.h',
  'pulse/error.h',
  'pulse/fork-detect.h',
  'pulse/format.h',
  'pulse/mainloop-api.h',
  'pulse/xmalloc.h',
  'pulse/proplist.h',
  'pulse/utf8.h',
  'pulse/channelmap.h',
  'pulse/sample.h',
  'pulse/util.h',
  'pulse/timeval.h',
  'pulse/rtclock.h',
  'pulse/volume.h',
  'pulsecore/atomic.h',
  'pulsecore/authkey.h',
  'pulsecore/conf-parser.h',
  'pulsecore/core-error.h',
  'pulsecore/core-format.h',
  'pulsecore/core-rtclock.h',
  'pulsecore/core-util.h',
  'pulsecore/creds.h',
  'pulsecore/dynarray.h',
  'pulsecore/endianmacros.h',
  'pulsecore/fdsem.h',
  'pulsecore/flist.h',
  'pulsecore/g711.h',
  'pulsecore/hashmap.h',
  'pulsecore/i18n.h',
  'pulsecore/idxset.h',
  'pulsecore/arpa-inet.h',
  'pulsecore/iochannel.h',
  'pulsecore/ioline.h',
  'pulsecore/ipacl.h',
  'pulsecore/json.h',
  'pulsecore/llist.h',
  'pulsecore/lock-autospawn.h',
  'pulsecore/log.h',
  'pulsecore/ratelimit.h',
  'pulsecore/macro.h',
  'pulsecore/mcalign.h',
  'pulsecore/mem.h',
  'pulsecore/memblock.h',
  'pulsecore/memblockq.h',
  'pulsecore/memchunk.h',
  'pulsecore/mutex.h',
  'pulsecore/native-common.h',
  'pulsecore/once.h',
  'pulsecore/packet.h',
  'pulsecore/parseaddr.h',
  'pulsecore/pdispatch.h',
  'pulsecore/pid.h',
  'pulsecore/pipe.h',
  'pulsecore/memtrap.h',
  'pulsecore/aupdate.h',
  'pulsecore/proplist-util.h',
  'pulsecore/pstream-util.h',
  'pulsecore/pstream.h',
  'pulsecore/queue.h',
  'pulsecore/random.h',
  'pulsecore/refcnt.h',
  'pulsecore/srbchannel.h',
  'pulsecore/sample-util.h',
  'pulsecore/semaphore.h',
  'pulsecore/shm.h',
  'pulsecore/bitset.h',
  'pulsecore/socket-client.h',
  'pulsecore/socket-util.h',
  'pulsecore/strbuf.h',
  'pulsecore/strlist.h',
  'pulsecore/tagstruct.h',
  'pulsecore/thread.h',
  'pulsecore/time-smoother.h',
  'pulsecore/time-smoother_2.h',
  'pulsecore/tokenizer.h',
  'pulsecore/usergroup.h',
  'pulsecore/sndfile-util.h',
  'pulsecore/socket.h',
]

if dbus_dep.found()
  libpulsecommon_sources += [
    'pulsecore/dbus-util.c',
    'pulsecore/rtkit.c',
  ]
  libpulsecommon_headers += [
    'pulsecore/dbus-util.h',
    'pulsecore/rtkit.h',
  ]
endif

if x11_dep.found()
  libpulsecommon_sources += [
    'pulse/client-conf-x11.c',
    'pulsecore/x11prop.c',
  ]
  libpulsecommon_headers += [
    'pulse/client-conf-x11.h',
    'pulsecore/x11prop.h',
  ]
endif

# FIXME: Do non-POSIX thread things
if host_machine.system() == 'windows'
  libpulsecommon_sources += [
    'pulsecore/mutex-win32.c',
    'pulsecore/poll-win32.c',
    'pulsecore/semaphore-win32.c',
    'pulsecore/thread-win32.c',
  ]
else
  libpulsecommon_sources += [
    'pulsecore/mutex-posix.c',
    'pulsecore/semaphore-posix.c',
    'pulsecore/thread-posix.c'
  ]
endif
# FIXME: Do SIMD things

if not get_option('client')
  libpulsecommon_dep = cc.find_library('pulsecommon-' + pa_version_major_minor, dirs : privlibdir, required : true)
  libpulse_dep = dependency('libpulse', required : true)
  libpulse_simple_dep = dependency('libpulse-simple', required : true)
else
  libpulsecommon = shared_library('pulsecommon-' + pa_version_major_minor,
    libpulsecommon_sources,
    libpulsecommon_headers,
    include_directories : [configinc, topinc],
    c_args : [pa_c_args],
    link_args : [nodelete_link_args],
    install : true,
    install_dir : privlibdir,
    dependencies : [
      libm_dep, thread_dep, dl_dep, shm_dep, iconv_dep, sndfile_dep, dbus_dep,
      x11_dep, libsystemd_dep, glib_dep.partial_dependency(compile_args: true),
      gtk_dep.partial_dependency(compile_args: true), asyncns_dep, libintl_dep,
      platform_dep, platform_socket_dep, execinfo_dep, libatomic_ops_dep,
    ],
    implicit_include_directories : false)

  libpulsecommon_dep = declare_dependency(link_with: libpulsecommon)

  subdir('pulse')
endif

if get_option('daemon')
  subdir('pulsecore')
  subdir('daemon')
  subdir('modules')
endif
if get_option('tests')
  subdir('tests')
endif
subdir('utils')
