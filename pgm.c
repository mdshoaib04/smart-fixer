#include <stdio.h>
int findLRU(int time[], int n) {
 int i, min = time[0], pos = 0;
 for (i = 1; i < n; i++) {
 if (time[i] < min) {
 min = time[i];
 pos = i;
 }
 }
 return pos;
}
int main() {
 int frames, pages, i, j, pos, page_faults = 0;
 int page[100], frame[10], time[10], counter = 0;
 printf("Enter number of pages: ");
 scanf("%d", &pages);
 printf("Enter the page reference string:\n");
 for (i = 0; i < pages; i++) {
 scanf("%d", &page[i]);
 }
 printf("Enter number of frames: ");
 scanf("%d", &frames);
 for (i = 0; i < frames; i++) {
 frame[i] = -1;
 time[i] = 0;
 }
 printf("\nPage\tFrames\n");
 for (i = 0; i < pages; i++) {
 int found = 0;
 // Check if page is already in frame
 for (j = 0; j < frames; j++) {
 if (frame[j] == page[i]) {
 found = 1;
 counter++;
 time[j] = counter; // update time
 break;
 }
 }
 if (!found) {
 int empty = -1;
 // Check for an empty frame
 for (j = 0; j < frames; j++) {
 if (frame[j] == -1) {
 empty = j;
 break;
 }
 }
 if (empty != -1) {
 frame[empty] = page[i];
 counter++;
 time[empty] = counter;
 } else {
 pos = findLRU(time, frames);
 frame[pos] = page[i];
 counter++;
 time[pos] = counter;
 }
 page_faults++;
 }
 // Print frame status
 printf("%d\t", page[i]);
 for(j = 0; j < frames; j++) {
 if (frame[j] != -1)
 printf("%d ", frame[j]);
 else
 printf("- ");
 }
 printf("\n");
 }
 printf("\nTotal Page Faults: %d\n", page_faults);
 return 0;
}