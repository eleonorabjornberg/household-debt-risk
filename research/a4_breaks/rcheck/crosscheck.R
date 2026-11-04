# A4 cross-check in R strucchange (pre-registration docs/decisions/breaks.md, "agreement with R strucchange", tolerance (b)).
# Rscript research/a4_breaks/rcheck/crosscheck.R   (R 4.3.3, strucchange 1.5.3, sandwich 3.1.0, Ubuntu archive)
suppressMessages({library(strucchange); library(sandwich)})
d <- read.csv("research/a4_breaks/rcheck/dy_total.csv")
y <- ts(d$dy)
n <- length(y); h <- floor(0.10 * n)
bp <- breakpoints(y ~ 1, h = h, breaks = 5)
rss <- summary(bp)$RSS
dates <- lapply(1:5, function(m) { b <- breakpoints(bp, breaks = m)$breakpoints; d$quarter[b + 1] })
# HAC F statistics for a single break at every admissible date (homogeneous long-run variance, sandwich::kernHAC defaults)
fs <- Fstats(y ~ 1, from = h, to = n - h, vcov. = kernHAC)
ci <- confint(bp, breaks = 1, vcov. = kernHAC)$confint
lines <- c(sprintf("n\t%d", n), sprintf("h\t%d", h))
for (m in 0:5) lines <- c(lines, sprintf("ssr_%d\t%.10f", m, rss["RSS", as.character(m)]), sprintf("bic_%d\t%.6f", m, rss["BIC", as.character(m)]))
for (m in 1:5) lines <- c(lines, sprintf("breaks_%d\t%s", m, paste(dates[[m]], collapse = ",")))
lines <- c(lines, sprintf("supF_hac_homogeneous\t%.6f", max(fs$Fstats)), sprintf("supF_hac_argmax\t%s", d$quarter[fs$breakpoint + 1]),
           sprintf("ci_1break_kernHAC_obs\t%d,%d,%d", ci[1, 1], ci[1, 2], ci[1, 3]))
writeLines(lines, "research/a4_breaks/rcheck/r_side.tsv")
cat(lines, sep = "\n")
