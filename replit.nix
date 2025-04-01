{pkgs}: {
  deps = [
    pkgs.unzip
    pkgs.zip
    pkgs.portaudio
    pkgs.libGLU
    pkgs.libGL
    pkgs.postgresql
    pkgs.openssl
  ];
}
