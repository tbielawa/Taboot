#!/usr/bin/ruby
# -*- coding: utf-8 -*-
# Release Builder - Ruby Scripts for building a software release
# Copyright © 2009-2011, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

load "maintainer-scripts/lib/builders.rb"
load "maintainer-scripts/lib/builddirector.rb"
load "maintainer-scripts/lib/utils.rb"

# This is a maintainer script intended to facilitate making
# releases. Word to the wise, it won't work for most people. You need
# a fedorahosted account and your system needs to be configured with
# the user certificates to communicate with Koji build systems.
#
# What does this really do? It automates the process of building RPMs
# for three different target platforms: RHEL5, RHEL6, and Fedora
# 14. This includes the building of the source RPMs with any
# appropriate flags for compatability, as well as submitting the
# source RPMs to a Koji build server which builds the binary RPMs.
#
# As an added bonus this script runs the SRPM builds and Koji uploads
# in parallel via subprocesses.
#
# Final note: The final step requires an external program called
# download-scratch.py. This will be the case until Taboot is in the
# Repos and can make non-scratch builds in Koji. download-scratch.py
# is available at:
# http://people.redhat.com/mikeb/scripts/download-scratch.py and
# should be placed in your $PATH.

class TabootBuilder < KojiBuilder
  def initialize(dist, build_target)
    super("python-taboot", `make version`.strip, %w"python-taboot taboot-func", dist, build_target)
    @sourcedir = "dist"
    @@sdist = "#{@sourcedir}/#{@full_name}.tar.gz"
    @@release_name = "taboot"
    @@package_release_dir = "/releases/#{@@release_name}-#{@version}"
    @@doc_release_dir = "/docs/#{@@release_name}-#{@version}"
  end

  def build_srpm
    cargs = self.compat_args.join(" ")
    build_command = "rpmbuild -bs #{cargs} --define \"dist .#{@dist}\" --define \"_sourcedir #{@sourcedir}\" #{@specfile}"

    puts "|-------------------------------------------------------------|"
    puts "| BUILDING SRPM for #{@dist} with this command:"
    puts "|    #{build_command}"
    puts "|-------------------------------------------------------------|"

    `#{build_command}`
  end
end

dists = %w"el5 el6 fc14"

builders = Array.new
builders.push TabootBuilder.new("el5", "dist-5E-epel")
builders.push TabootBuilder.new("el6", "dist-6E-epel")
builders.push TabootBuilder.new("fc14", "dist-f14")
builders.push TabootBuilder.new("fc15", "dist-f15")

director = BuildDirector.new(builders)

if ARGV.include? "srpm"
  director.build_srpms
  srpm_path = builders.first.srpm_path
  full_name = builders.first.package_name

  results = dists.collect do |dist|
    glob = "#{srpm_path}/#{full_name}*#{dist}.src.rpm"
    Dir[glob]
  end

  puts "SRPMs created. You can pick them up here:"
  puts results
else
  # Other options you could use are:
  #  director.list_builders
  #  director.build_docs
  #  director.build_srpms
  #  director.build_rpms

  # Build docs, srpms, rpms, and make a release folder with all the
  # generated items.
  director.start_build
end

