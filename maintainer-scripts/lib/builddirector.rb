# -*- mode: ruby -*-


class BuildDirector
  def initialize(builders)
    # In the future this should work like a queue with a configurable
    # level of concurrency
    @builders = builders
  end

  def start_build
    puts "|=============================================================|"
    puts "| Running mock build processes to generate SRPMs now"
    puts "| (This could take a little while...)"
    puts "|=============================================================|"
    @builders.each do |builder|
      fork do
        builder.build_srpm
      end
    end
    Process.waitall

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
