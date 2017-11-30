#!/usr/bin/perl

use strict;
use warnings;

# Get the list of docker images
my @list = `docker image ls -a`;

my @images;
foreach my $i ( @list ){
    if( $i =~ /^<none>.+\s(([0-9]|[a-f]){12})\s/ ){
        push @images, $1;
    }  
}

# delete images
for my $i ( @images ){
    print "docker rmi $i\n";
    @list = `docker rmi $i 2>&1`;
    print "@list";
    for my $j ( @list ){
        if( $j =~ /stopped\scontainer\s(([0-9]|[a-f]){12})/ ){
            my $container = $1;
            print "docker rm $container\n";
            my @list2 = `docker rm $container 2>&1`;
            print "@list2";
            @list = `docker rmi $i 2>&1`;
            print "@list";
        }
    }
}
