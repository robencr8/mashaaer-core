{pkgs}: {
  deps = [
    pkgs.libyaml
    pkgs.python312Packages.pyngrok
    pkgs.iproute2
    pkgs.geckodriver
    pkgs.pkg-config
    pkgs.mtdev
    pkgs.libcxx
    pkgs.SDL2_ttf
    pkgs.SDL2_mixer
    pkgs.SDL2_image
    pkgs.SDL2
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
