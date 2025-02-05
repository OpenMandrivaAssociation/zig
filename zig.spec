%global _lto_cflags %{nil}
%global __builder   ninja
%bcond_without  macro
%bcond_without  test

Name:           zig
Version:        0.14.0~20250205
Release:        1
Summary:        Compiler for the Zig language
License:        MIT
Group:          Development/Languages/Other
URL:            https://ziglang.org/
#Source0:        https://ziglang.org/download/%{version}/%{name}-%{version}.tar.xz
Source0:	zig-0.14.0-20250205.tar.xz
Source1:        macros.%{name}
# The vendored tarball is for tests. This contains the
# cached deps. See https://en.opensuse.org/Zig#Packaging
#Source2:        vendor.tar.zst
Source3:        zig-rpmlintrc
#Patch0:         0000-remove-lld-in-cmakelist.patch
#Patch1:         0001-invoke-lld.patch
#Patch2:         0002-no-lld-libs-and-includes.patch
# Just copying from Archlinux. Thanks
#Patch3:         https://gitlab.archlinux.org/archlinux/packaging/packages/zig/-/raw/main/skip-localhost-test.patch

BuildRequires:  cmake
BuildRequires:  elfutils
BuildRequires:  glibc
BuildRequires:  glibc-devel
BuildRequires:  help2man
BuildRequires:  pkgconfig(libelf)
BuildRequires:  liburing-devel
BuildRequires:  mold
BuildRequires:  ninja
BuildRequires:  pkgconfig(zlib)
BuildRequires:  zstd
BuildRequires:	llvm-devel
BuildRequires:	clang
BuildRequires:  cmake(Clang)
BuildRequires:  cmake(LLD)
BuildRequires:	lld

# Zig needs this to work
Requires:       %{name}-libs = %{version}

# Zig Macros
Recommends:     %{name}-rpm-macros

%description
General-purpose programming language and toolchain for maintaining robust, optimal, and reusable software.

* Robust - behavior is correct even for edge cases such as out of memory.
* Optimal - write programs the best way they can behave and perform.
* Reusable - the same code works in many environments which have different constraints.
* Maintainable - precisely communicate intent to the compiler and other programmers.
The language imposes a low overhead to reading code and is resilient to changing requirements and environments.

%package libs
Summary:        Zig Standard Library
BuildArch:      noarch

%description libs
%{name} Standard Library

%if %{with macro}
%package        rpm-macros
Summary:        Common RPM macros for %{name}
Requires:       rpm
BuildArch:      noarch

%description    rpm-macros
This package contains common RPM macros for %{name}.
%endif

%prep
%autosetup -n %{name}-0.14.0-20250205 -p1 
#-a2
%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_LINKER_TYPE=MOLD \
  -DZIG_SHARED_LLVM=On \
  -DZIG_USE_LLVM_CONFIG=ON \
  -DZIG_TARGET_MCPU="baseline" \
  -DZIG_VERSION:STRING="0.14.0"

%make_build

%install
%make_install -C build
mkdir -p %{buildroot}%{_mandir}/man1
help2man --no-discard-stderr "%{buildroot}%{_bindir}/%{name}" --version-option=version --output=%{buildroot}%{_mandir}/man1/%{name}.1

mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d/
install -p -m644 %{SOURCE1} %{buildroot}%{_rpmmacrodir}

sed -i -e "s|@@ZIG_VERSION@@|%{version}|"  %{buildroot}%{_rpmmacrodir}/macros.%{name}

mv -v doc/langref.html.in doc/langref.html

%if 0%{?with test}
%check
./build/stage3/bin/zig build test -Dconfig_h=build/config.h \
	-Dcpu=baseline \
	-Dskip-debug \
	-Dskip-release-safe \
	-Dskip-release-small \
        -Dstatic-llvm=false \
	-Denable-llvm=true \
	-Dskip-non-native=true
%endif

%files
%license LICENSE
%{_bindir}/zig
%{_mandir}/man1/%{name}.1%{?ext_man}
%doc README.md
%doc lib/docs
%doc doc/langref.html

%files libs
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/*

%if %{with macro}
%files rpm-macros
%{_rpmmacrodir}/macros.%{name}
%endif
