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


class BuildDirector
  def initialize(builders)
    # In the future this should work like a queue with a configurable
    # level of concurrency
    @builders = builders
    @release_name = @builders.first.release_name
    @release_dir = @builders.first.release_dir
    @version = @builders.first.version
    @doc_dir = @release_dir + @builders.first.doc_release_dir
    @sdist = @builders.first.sdist
    @builders.first.setup_sdist
    @package_release_dir = @builders.first.package_release_dir
  end

  def build_docs
    build_command = "./setup.py doc"
    doc_path = File.expand_path "./docs/html"

    # run the build command
    `#{build_command}`

    # Need to make target doc dir
    FileUtils.mkdir_p "#{@release_dir}/docs/"

    # Move docs/html to @doc_dir/
    FileUtils.mv File.expand_path("./docs/html"), @doc_dir

    # Make a tar.gz of the docs in their new renamed dir
    FileUtils.cd File.expand_path("#{@release_dir}/docs") do |p|
      # Like "taboot-0.2.9"
      doc_dist = "#{@release_name}-#{@version}"
      tar_command = "tar -czf #{doc_dist}.tar.gz #{doc_dist}"

      puts "Building doc archive with: #{tar_command}"
      `#{tar_command}`

      puts "Generated docs: "
      puts "   - #{@doc_dir}"
      puts "   - #{@doc_dir}.tar.gz"
    end
  end

  def build_srpms
    puts "|=============================================================|"
    puts "| Running rpmbuild processes to generate SRPMs now"
    puts "|=============================================================|"
    @builders.each do |builder|
      fork do
        result = builder.build_srpm
      end
    end
    Process.waitall
  end

  def build_rpms
    puts "|=============================================================|"
    puts "| Running Koji build processes to generate RPMs now"
    puts "| (This could take a little while...)"
    puts "|=============================================================|"
    @builders.each do |builder|
      fork do
        builder.build_rpm
      end
    end
    Process.waitall

    FileUtils.cp @sdist, @release_dir + @package_release_dir
  end

  def start_build
    self.list_builders
    self.build_docs
    self.build_srpms
    self.build_rpms
    puts ""
    puts "Build complete! You can pick up your data:"
    puts "    #{@release_dir}"
  end

  def list_builders
    puts "Director has #{@builders.count} registered builders"
    puts "---------------------------------------------------"
    @builders.each do |builder|
      puts builder
      puts
    end
  end
end
