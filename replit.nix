{pkgs}: {
  deps = [
    pkgs.jq
    pkgs.unzip
    pkgs.zip
    pkgs.portaudio
    pkgs.libGLU
    pkgs.libGL
    pkgs.postgresql
    pkgs.openssl
  ];
}
