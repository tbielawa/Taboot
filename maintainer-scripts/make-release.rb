#!/usr/bin/ruby

load "maintainer-scripts/lib/builders.rb"
load "maintainer-scripts/lib/builddirector.rb"

# This is a maintainer script intended to facilitate making
# releases. Word to the wise, it won't work for most people. You need
# a fedorahosted account and your system needs to be configured with
# the user certificates to communicate with Koji build systems.
#
# What does this really do? It automates the process of building RPMs
# for three different target platforms: RHEL5, RHEL6, and Fedora
# 14. This includes the building of the source RPMs in a mock chroot,
# as well as submitting the source RPMs to a Koji build server which
# builds the binary RPMs.
#
# As an added bonus this script runs the SRPM builds and Koji uploads
# in parallel via subprocesses.

class TabootBuilder < KojiBuilder
  def initialize(mock_chroot, build_target)
    super("python-taboot", `make version`.strip, mock_chroot, build_target)
  end
end

builders = Array.new
builders.push TabootBuilder.new("epel-5-i386", "dist-5E-epel")
builders.push TabootBuilder.new("epel-6-i386", "dist-6E-epel")
builders.push TabootBuilder.new("fedora-14-i386", "dist-f14")

director = BuildDirector.new(builders)
director.list_builders
director.start_build
