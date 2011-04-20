# -*- coding: utf-8 -*-
# -*- mode: ruby -*-
# Release Builder - Ruby Scripts for building a software release
# Copyright © 2011, Red Hat, Inc.
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


# The builders make some assumptions about how things are configured
# in your project. This class provides a good base class though, and
# subclassing is intended to make the scripts fit any specific
# needs. See ../make-release.rb for examples of how you might do that.

require 'tempfile'
require 'net/http'
require 'fileutils'

class Builder
  @rpm_build_command = ""
  def initialize(package_name, version, target_rpms, dist, koji_build_target)
    @package_name = package_name
    @version = version
    @dist = dist
    @full_name = "#{@package_name}-#{@version}"
    @build_target = koji_build_target
    @srpm_path = File.expand_path("~/rpmbuild/SRPMS")
    @sourcedir = File.expand_path("~/rpmbuild/SOURCES")
    @specfile = "#{@package_name}.spec"
    @srpm = nil
    @target_rpms = target_rpms

    # Class variables
    @@task_ids = Tempfile.new "builder."
    @@release_dir = Dir.mktmpdir "builder."
    @@release_name = @package_name
    @@package_release_dir = "/releases/#{@@release_name}-#{@version}"
    @@doc_release_dir = "/docs/#{@@release_name}-#{@version}"
    @@sdist = "#{@sourcedir}/#{@full_name}.tar.gz"
  end

  def setup_sdist
    sdist_result = `./setup.py sdist`
  end

  def compat_args
    # If building RHEL 5 source RPMs you might run into problems on
    # newer systems if you're not chrooted. See this bug report:
    # https://bugzilla.redhat.com/show_bug.cgi?id=490613 for more
    # information.
    cargs = Array.new
    if @dist == "el5"
      cargs.push "--define \"_source_filedigest_algorithm md5\""
      cargs.push "--define \"_binary_filedigest_algorithm md5\""
    end
    return cargs
  end

  def build_srpm
    cargs = self.compat_args.join(" ")
    build_command = "rpmbuild -bs #{cargs} --define \"dist .#{@dist}\" #{@specfile}"

    puts "|-------------------------------------------------------------|"
    puts "| BUILDING SRPM for #{@dist} with this command:"
    puts "|    #{build_command}"
    puts "|-------------------------------------------------------------|"

    `#{build_command}`
    return self.srpm
  end

  def build_rpm
    # There is probably a better way to do this
    result_glob = "#{@srpm_path}/#{@full_name}*#{@dist}.src.rpm"
    results = Dir[result_glob]

    if results.first.nil?
      # nil happens when the source RPM couldn't be built. Bail
      # out. Bail out now!
      return nil
    else
      @srpm = results.first
    end

    build_command = "#{@rpm_build_command} build --nowait --noprogress --scratch #{@build_target} #{@srpm}"
    puts "|-------------------------------------------------------------|"
    puts "| BUILDING RPM for #{@build_target} with this command:"
    puts "|    #{build_command}"
    puts "|-------------------------------------------------------------|"

    @task_id = nil
    status_url = nil

    # Instead of the normal `backtick` command execution we're using
    # IO.popen here because it's the simplest way to actually capture
    # the stdout and stderr from Koji.
    IO.popen(build_command) do |build_process|
      # Iterate over each line of Koji output. Koji doesn't seem to
      # flush it's stderr often so this will not be a continuous
      # flow. That doesn't matter very much anyway since this should
      # only take as long as is required to upload the srpm.
      build_process.each do |line|
        # Get the info so we can consolidate and report it
        if line.scan(/(Created).*?([0-9]+)/).count > 0
          @task_id = line.scan(/(Created).*?([0-9]+)/)[0][1]
        elsif line.scan(/http.*$/).count > 0
          status_url = line.match(/http.*$/)[0]
        else
          puts line
        end
      end
    end

    puts "|-------------------------------------------------------------|"
    puts "| KOJI JOB SUBMITTED. Building with task id: #{@task_id}"
    puts "| Track the progress of this build at this url:"
    puts "|    #{status_url}"
    puts "|-------------------------------------------------------------|"

    self.poll_task_state
  end

  def poll_task_state
    @task_status = "open"

    poll_command = "#{@rpm_build_command} taskinfo #{@task_id}"

    while @task_status == "open" or @task_status == "free"
      sleep 4
      print  "Polling #{@task_id}... "
      IO.popen(poll_command) do |poll_status|
        poll_status.each do |line|
          koji_output = line.scan(/^(State: )(.*)/)
          if koji_output.count > 0
            @task_status = koji_output[0][1]
            puts @task_status
          end
        end
      end
    end

    # open/closed/failed
    puts "Koji build finished with a state of: #{@task_status}"

    # If the task finished with a 'closed' state we can start
    # downloading the target_rpms.
    if @task_status == "closed"
      self.download_target_rpms
    else
      puts "BUILD FAILED! You probably should check that out."
    end
  end

  def download_target_rpms
    local_download_path = @@release_dir + @@package_release_dir
    FileUtils.mkdir_p local_download_path
    # Unfortunately, until some patches are incorporated into an
    # upcoming Koji release we have to fall back to this external
    # script for download scratch build results.
    download_command = "download-scratch.py #{@task_id}"
    result_glob = "*.rpm"

    puts "Downloading results with command: #{download_command}"
    `#{download_command}`

    results = Dir[result_glob]
    FileUtils.mv results, local_download_path
    puts "Build results downloaded to #{local_download_path}"
  end

  def srpm
    result_glob = "#{@srpm_path}/#{@full_name}*#{@dist}.src.rpm"
    results = Dir[result_glob]

    if results.first.nil?
      # nil happens when the source RPM couldn't be built. Bail
      # out. Bail out now!
      return nil
    else
      @srpm = results.first
    end
    @srpm
  end

  def to_s
    builder_properties = "#{@package_name} (#{@version})\n"
    builder_properties << "Build target: #{@build_target}\n"
    builder_properties << "Target RPMs: #{@target_rpms.join(", ")}"
  end

  attr_accessor :package_name, :version, :srpm_path, :sourcedir

  def release_name
    @@release_name
  end

  def release_dir
    @@release_dir
  end

  def doc_release_dir
    @@doc_release_dir
  end

  def sdist
    @@sdist
  end
end


class BrewBuilder < Builder
  def initialize(package_name, version, target_rpms, dist, koji_build_target)
    super(package_name, version, target_rpms, dist, koji_build_target)
    @rpm_build_command = "brew"
  end
end


class KojiBuilder < Builder
  def initialize(package_name, version, target_rpms, dist, koji_build_target)
    super(package_name, version, target_rpms, dist, koji_build_target)
    @rpm_build_command = "koji"
  end
end
