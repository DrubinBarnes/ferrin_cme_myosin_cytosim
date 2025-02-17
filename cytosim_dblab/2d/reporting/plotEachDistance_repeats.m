% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/crosslinkRates_1to20')

%% for repeats of a simulation

% clear;

% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/crosslinking_lengths_endo')
% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/arpVary_0-1000_output')
% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/nucleationVary_output')
%  cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/motherFilament__diffuseFast_stickyx15_output')
% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/3D_repat24x_plusCrosslinking')

% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/motherFilament_bind1000_2')
% cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/springStiffnessVary')
 cd('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/hip1R_toggle_0hip1R_output')

% fimRate = 1:20;

% arpNb = [0 1 10 25 50:50:500 1000];
% nucleationRate = [0.001 0.01 1 5 7 10 100 1000 10000];

springStiffness = 0.15 % pN nm
% membraneTension = 

timeStep = 0.1 %s (default)

allTracks = dir('soliddistances_track*');

timesFile = dir('solid times.txt');
times = textread(timesFile.name);

%     curMeanTextFileName = [allNames{i} 'meanDistance10beads.txt'];
%     curStdTextFileName  = [allNames{i} 'stdDistance10beads.txt'];
%     currentTimesFileName= [allNames{i} 'times.txt'];
%     
%     currentMeanTextFile = textread(curMeanTextFileName);
%     currentStdTextFile  = textread(curStdTextFileName);
%     currentTimesTextFile= textread(currentTimesFileName);
%     
%     allMeans{i} = currentMeanTextFile;
%     allStds{i}  = currentStdTextFile;
%     allTimes{i} = currentTimesTextFile;
    
nbTracks = length(allTracks);
eachTrack = {};

myColors = parula(nbTracks+1);



for n=1:nbTracks
    
    curTrack = textread(allTracks(n).name);
    eachTrack(n).Distances = curTrack;
end

finalDistances = [];
% final distance
for n=1:nbTracks
    finalDistances(n) = eachTrack(n).Distances(end);
end

%% average all tracks

% meanDistance = [];
% stdDistance  = [];
% 
% for n = 1:nbTracks
%     
% end

%% plot final distance vs inputparam (in this case fimDistance)

% figure(3);clf;
% 
% plot(fimRate,-finalDistances-1.5, 'ok')
% 
% xlabel('Fimbrin on rate (s^-1)');
% ylabel('Internalization distance (µm)');
% set(gca,'FontSize',15)
% 
% ylim([0 0.1])


%% calculate time retrating

% set a window to look (can average this later)

secPerFrame = 0.1;

distanceWindow = 0.5; % in s
distanceWindowFrames = distanceWindow/secPerFrame



%% divide into subplots

nbSubplots = 4;

% for n = 1:nbSubplots
bin1 = 1:5;
bin2 = 6:10;
bin3 = 11:15;
bin4 = 16:20;

% bin1 = 1:floor(nbTracks/nbSubplots);
% bin2 = floor(nbTracks/nbSubplots)+1:floor(nbTracks/nbSubplots*2);
% bin3 = floor(nbTracks/nbSubplots/2)+1:floor(nbTracks/nbSubplots*3/2);
% bin4 = floor(nbTracks/nbSubplots*3/2)+1:nbTracks;

figure(11); clf;

for n = 1:nbTracks
    
    figure(11); hold on;
%     subplot(4,1,1)
    plot(timeStep:timeStep:timeStep*length(eachTrack(n).Distances),(eachTrack(n).Distances)*1000, 'Color', myColors(n,:), 'LineWidth', 1.5)
end

figure(11);
set(gca,'FontSize', 16)
set(gca,'box','on')
xlabel('Time (s)')
ylabel('Distance (nm)')

% add NaNs til 10 s, convert to nm

nbPts = 15/timeStep;

for n = 1:nbTracks
    
    curLastIndex =  length(eachTrack(n).Distances);
    eachTrack(n).Distances_nm = [(eachTrack(n).Distances)*1000; NaN(nbPts-curLastIndex,1)];
end
    
% average

% for m=1:10/timeStep

allTracksCurTimept = []

    for n = 1:nbTracks
        
        allTracksCurTimept(:,n) = eachTrack(n).Distances_nm;
        
    end
    avgTracks = nanmean(allTracksCurTimept,2);
    stdTracks = nanstd(allTracksCurTimept,[],2);

    % fill in nan for any time points with just one data point
    mm = 1;
    lastTimepts=repmat(length(avgTracks),nbTracks,1);
    for m = 1:length(stdTracks)
        if stdTracks(m)==0
            avgTracks(m) = NaN;
            lastTimepts(mm) = m;
            mm = mm+1;
        end
    end
    lastTimept = lastTimepts(1);
%% plot av and std

figure(12);clf;

times = 0.1:timeStep:15;

    [h, p] = boundedline(times(1:lastTimept-1)', avgTracks(1:lastTimept-1), stdTracks(1:lastTimept-1), '.k', 'alpha'); 
    outlinebounds(h,p)

set(gca,'FontSize', 16)
set(gca,'box','on')
xlabel('Time (s)')
ylabel('Vesicle distance (nm)')
ylim([-100 5])

%% plot energy required to internalize

% based on force * internalization "distance" (pN nm)

% force [pN] is distance [nm] * spring stiffness (pN/nm) 

% so energy [pN nm] is 1/2 * distance [nm] * distance [nm] * spring stifness [pN/nm]

for n = 1:nbTracks

    eachTrack(n).internalizationEnergy = 0.5* eachTrack(n).Distances_nm .* eachTrack(n).Distances_nm .* springStiffness;

end

 figure(55); clf;

for n = 1:nbTracks

   hold on; plot(eachTrack(n).internalizationEnergy)
end

allTracksEnergy = []

    for n = 1:nbTracks
        
        allTracksEnergy(:,n) = eachTrack(n).internalizationEnergy;
        
    end
    avgEnergyTracks = nanmean(allTracksEnergy,2);
    stdEnergyTracks = nanstd(allTracksEnergy,[],2);

    % fill in nan for any time points with just one data point
    mm = 1;
    lastTimepts=repmat(length(avgEnergyTracks),nbTracks,1);
    for m = 1:length(stdEnergyTracks)
        if stdEnergyTracks(m)==0
            avgEnergyTracks(m) = NaN;
            lastTimepts(mm) = m;
            mm = mm+1;
        end
    end
    lastTimept = lastTimepts(1);

    figure(54);hold on;
        
    subplot(1,2,2)
    alltimes = timeStep*(1:length(avgEnergyTracks));

    errorbar(alltimes, avgEnergyTracks,stdEnergyTracks)
       ylabel('Internalization energy (pN nm)');
set(gca,'FontSize',15)
xlabel('Time (s)')
set(gca,'box','on')
ylim([-50 1000])
xlim([0 15])
% for a given coat rigidity, too.

%% plot final distance 

figure(5);clf;

plot(nucleationRate, -(finalDistances+1.5)*1000, '-ok', 'LineWidth', 1.5);
set(gca,'FontSize', 16)
set(gca,'box','on')
xlabel('Number Arp2/3 complex')
ylabel('Final distance internalized (nm)')


figure(2);clf;

bins={bin1,bin2,bin3,bin4};
nn = 1;
for m = 1:length(bins)
    
    for n=bins{m}
        figure(2); hold on;
        subplot(1,nbSubplots,m)
        plot(timeStep:timeStep:timeStep*length(eachTrack(n).Distances),eachTrack(n).Distances+1.5, 'Color', myColors(nn,:))
        nn = nn+1;
        ylim([-0.1 0.01])
        set(gca,'FontSize', 15)
        xlabel(['time (s)'])
        ylabel(['Vesicle distance (µm)'])
    end
end

figure(4); clf;

for n = [1,5,10,15,20]
    figure(4);hold on; 
    plot(timeStep:timeStep:timeStep*length(eachTrack(n).Distances),eachTrack(n).Distances+1.5, 'Color', myColors(n,:))
end
ylim([-0.1 0.01])
        set(gca,'FontSize', 15)
        set(gca,'box','on')
        xlabel(['time (s)'])
        ylabel(['Vesicle distance (µm)'])