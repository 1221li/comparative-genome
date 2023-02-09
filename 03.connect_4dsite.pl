#!/usr/bin/perl
use strict;
use Data::Dumper;
die "Usage : perl $0 <split.fa> <merge.fa>\n" unless @ARGV == 2;
open (IN,"$ARGV[0]") or die "permission denied\n";
open (OUT,">$ARGV[1]") or die "permission denied\n";

my %hash;
local $/ = '>';
<IN>;
my ($head, $seq,@sequence,@novel_name);
while(<IN>){
	s/\r?\n>?$//;
	( $head, $seq ) = split /\r?\n/, $_, 2;
	$seq =~ s/\s+//g;
	push @{$hash{$head}},$seq;
}
close IN;
 $/ = "\n";
 
 foreach my $head(sort{$a<=>$b}keys %hash){
	my @tmp_array = @{$hash{$head}};
	my $seq = join("",@tmp_array);
	print OUT ">$head\n$seq\n";
}
close IN;
close OUT;