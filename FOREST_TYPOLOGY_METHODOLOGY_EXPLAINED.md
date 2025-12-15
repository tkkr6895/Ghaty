# Forest Typology Analysis - Methodology Explanation

**Date**: December 14, 2024  
**Analysis Area**: Western Ghats  
**Issue Identified**: Critical methodological error in probability threshold handling

---

## 🚨 CRITICAL FINDING: INCORRECT PROBABILITY HANDLING

### The Problem

The analysis script **incorrectly treated the Nature-Trace Natural Forest 2020 dataset as a binary (0/1) classification** when it is actually a **probabilistic dataset with values 0-250**.

**What happened:**
```python
# WRONG (what the script did):
natural_forest_area = natural_forest_2020.eq(1)  # Only counts pixels with value exactly 1

# CORRECT (what should have been done):
natural_forest_area = natural_forest_2020.gte(130)  # Probability >= 0.52 (52%)
```

**Impact:** We **severely UNDERESTIMATED natural forests** by only counting pixels with value = 1, which likely represent only the HIGHEST confidence pixels, missing the vast majority of natural forest area.

---

## 📊 Current Results (UNRELIABLE)

From the outputs you downloaded:

| Category | Area (km²) | Percentage | Pixels |
|----------|-----------|------------|--------|
| **No Trees (Class 0)** | 15.87 | 39.7% | 17,628 |
| **Plantations (Class 1)** | 22.65 | 56.6% | 25,169 |
| **Natural Forest (Class 2)** | 1.38 | 3.4% | 1,532 |
| **Old-Growth (Class 3)** | 0.11 | 0.3% | 121 |
| **TOTAL** | 40.01 | 100% | 44,450 |

**These numbers are WRONG** because:
- Natural forest shows only **3.4%** of the area
- This only captured pixels with probability value = 1
- Missed all pixels with probabilities 2-250 (which includes high-confidence natural forest)

---

## 📚 Nature-Trace Dataset Explanation

### What is Nature-Trace Natural Forest 2020?

A **probabilistic map** developed by Google DeepMind using AI/ML models to identify natural forests globally at 10m resolution.

**Key characteristics:**
1. **Probability values**: 0-250 (representing 0.0 to 1.0 probability, scaled by 250)
2. **Threshold**: Optimal threshold is **130** (= 52% probability) per official documentation
3. **What it classifies as "Natural Forest"**:
   - Primary forests (old-growth, undisturbed)
   - Naturally regenerating secondary forests
   - Managed natural forests (e.g., selective logging but natural regeneration)

**What it EXCLUDES (classified as non-natural):**
- Planted forests (timber plantations, pulpwood)
- Tree crops (oil palm, rubber, coffee with shade trees)
- Orchards and agroforestry
- Urban parks with planted trees

### How Probability Works

| Value Range | Probability | Interpretation |
|-------------|-------------|----------------|
| 0 | 0% | Definitely NOT natural forest |
| 1-50 | 0.4-20% | Very low confidence |
| 51-100 | 20-40% | Low confidence |
| 101-129 | 40-51.6% | Below recommended threshold |
| **130-200** | **52-80%** | **High confidence natural forest** |
| 201-250 | 80-100% | Very high confidence |

**Recommended usage** (per GEE documentation):
```javascript
var natural_forest = probabilities.gte(130);  // >= 52% probability
```

---

## 🌳 Forest Typology Categories Explained

### 1. **Natural Forest (Class 2)**

**Definition**: Forests that regenerated naturally, not planted by humans

**Current methodology (INCORRECT):**
- Counted only pixels where Nature-Trace value = 1
- This is essentially empty (only 1.38 km²)

**Corrected methodology (should be):**
- Nature-Trace probability >= 130 (52% threshold)
- Expected result: **Much larger area**, likely 40-60% of forested pixels

**Examples**:**
- Old-growth evergreen forests in Western Ghats (Nilgiris, Silent Valley)
- Secondary forests regrowing after abandonment
- Managed forests with natural regeneration (e.g., selective logging areas)

---

### 2. **Plantations (Class 1)**

**Definition**: Tree cover that is NOT natural forest

**Current methodology:**
```python
plantation_mask = trees_2023.And(natural_forest_mask.Not())
```
Where:
- `trees_2023` = Dynamic World tree cover 2023 (probability > 0.5)
- `natural_forest_mask` = Nature-Trace (incorrectly using == 1)

**Result:** Shows **22.65 km²** (56.6%) as plantations

**What this ACTUALLY captures:**
- Commercial timber plantations (eucalyptus, teak, acacia)
- Coffee/tea estates with shade trees
- Rubber plantations
- Tree crops
- **PLUS all the natural forests missed by the incorrect threshold!**

**Why the result is wrong:**
Since we only counted Nature-Trace = 1 as natural, almost ALL other forest got misclassified as "plantation", including:
- Natural forests with probability 2-129 (below our incorrect threshold)
- Natural forests with probability 130-250 (should be included!)

---

### 3. **Old-Growth Forest (Class 3)**

**Definition**: High-integrity natural forests that have remained undisturbed

**Current methodology:**
```python
old_growth_mask = natural_forest_mask \
    .And(treecover_2000.gt(70)) \      # High canopy in 2000
    .And(forest_loss.eq(0))             # No loss since 2000
```

**Result:** Only **0.11 km²** (0.27% of area)

**Why so small:**
1. Started with already-incorrect natural forest mask (== 1)
2. Further filtered to only pixels with:
   - Hansen tree cover > 70% in year 2000
   - Zero forest loss 2000-2023

**What this SHOULD show:**
- Primary forests in protected areas (e.g., within sanctuaries)
- Undisturbed forest patches on steep slopes
- Old-growth stands in sacred groves

---

### 4. **Forest Typology Composite (Class 0-3)**

**What the output represents:**

| Class | Category | Current Area | % | What it SHOULD be |
|-------|----------|--------------|---|-------------------|
| **0** | No trees | 15.87 km² | 39.7% | Non-forest (correct) |
| **1** | Plantation | 22.65 km² | 56.6% | Only actual plantations (~10-20%) |
| **2** | Natural | 1.38 km² | 3.4% | Natural forests (~40-60%) |
| **3** | Old-growth | 0.11 km² | 0.3% | Primary forests (~5-15%) |

---

## 🔧 How the Analysis SHOULD Work

### Corrected Methodology:

```python
# 1. Load Nature-Trace with CORRECT probability handling
natural_forest_col = ee.ImageCollection(
    'projects/nature-trace/assets/forest_typology/natural_forest_2020_v1_0_collection'
)
natural_forest_prob = natural_forest_col.mosaic().select('B0')  # Probability band

# 2. Apply recommended threshold (52% = value 130)
natural_forest_mask = natural_forest_prob.gte(130)

# OPTIONAL: Create confidence levels
high_conf_natural = natural_forest_prob.gte(200)  # >= 80% probability
medium_conf_natural = natural_forest_prob.gte(130).and(natural_forest_prob.lt(200))
low_conf_natural = natural_forest_prob.gte(100).and(natural_forest_prob.lt(130))

# 3. Load current tree cover (Dynamic World 2023)
trees_2023 = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
    .filterDate('2023-01-01', '2023-12-31') \
    .select('trees').mean().gt(0.5)

# 4. Derive plantations
# Plantation = Trees in 2023 but NOT natural forest
plantation_mask = trees_2023.And(natural_forest_mask.Not())

# 5. Identify old-growth (high integrity natural forests)
hansen = ee.Image('UMD/hansen/global_forest_change_2023_v1_11')
old_growth_mask = natural_forest_mask \
    .And(hansen.select('treecover2000').gt(70)) \  # High canopy 2000
    .And(hansen.select('loss').eq(0))               # No loss

# 6. Create composite classification
forest_typology = ee.Image(0) \
    .where(plantation_mask, 1) \
    .where(natural_forest_mask, 2) \
    .where(old_growth_mask, 3)
```

### Expected Corrected Results:

Based on Western Ghats ecology, we should see:
- **Natural forests**: 40-60% of forested area (not 3.4%!)
- **Plantations**: 10-30% (commercial plantations, tree crops)
- **Old-growth**: 5-15% (protected areas, inaccessible regions)
- **Non-forest**: 30-50% (agriculture, built-up, grasslands)

---

## 🎯 Why "Old-Growth" vs. "Natural Forest" Distinction?

### Natural Forest (broader category)
- Includes ALL forests that regenerated naturally
- Can include secondary forests (regrown after disturbance)
- Can include managed forests (e.g., selective logging)
- May have SOME human intervention but natural regeneration

### Old-Growth Forest (subset of natural)
- **High integrity** forests
- Minimal human disturbance
- Continuous forest cover since at least 2000
- High canopy cover (>70%)
- Ecological importance: Highest biodiversity, carbon storage, watershed protection

**Why distinguish them?**
1. **Conservation priority**: Old-growth is IRREPLACEABLE (takes 100+ years to develop)
2. **Biodiversity**: Old-growth harbors endangered species (lion-tailed macaque, Nilgiri tahr)
3. **Carbon storage**: Old-growth stores 2-3x more carbon than secondary forests
4. **Policy**: Different protection levels (old-growth should have strictest protection)

---

## 📈 Multi-Source Validation Strategy

### Why use multiple datasets?

Each dataset has strengths/weaknesses:

| Dataset | Strength | Weakness |
|---------|----------|----------|
| **Nature-Trace 2020** | AI-based, designed to separate natural/planted | Single year (2020), newer dataset |
| **Hansen GFC** | Long time series (2000-2023), loss/gain | Doesn't distinguish natural/plantation |
| **Dynamic World** | Daily updates, 10m resolution | Only 2016-present, includes all trees |
| **GLC-FCS30D** | Historical baseline (1985-2020) | Coarser classes, 30m resolution |

### Consensus Approach:

**High-confidence natural forest:**
- Nature-Trace >= 130 (52%)
- AND Hansen treecover2000 > 50
- AND GLC shows forest class in 1987
- = **Primary/old-growth natural forest**

**Medium-confidence natural forest:**
- Nature-Trace >= 130
- AND DW shows trees in 2023
- BUT Hansen shows gain OR not in GLC 1987
- = **Secondary natural forest** (regrown after clearing)

**High-confidence plantation:**
- Hansen gain = 1 (forest gain 2000-2012)
- AND DW shows trees in 2023
- AND Nature-Trace < 130
- = **Planted forests** post-2000

**Derived plantation:**
- DW shows trees 2023
- AND Nature-Trace < 130
- AND NO Hansen gain
- = **Older plantations** or tree crops (pre-2000)

---

## ⚠️ Limitations to Acknowledge

### Nature-Trace Known Issues:
1. **Agroforestry confusion**: Shade-grown coffee/cardamom can be misclassified as natural
2. **Boreal/temperate bias**: Less accurate in uniform plantations (eucalyptus monocultures)
3. **Post-disturbance ambiguity**: Recently logged forests unclear if they'll regenerate naturally
4. **Input data quality**: Training data had mixed quality/resolution

### Hansen Limitations:
1. **Gain band**: Only captures 2000-2012 (misses recent plantations)
2. **No forest type**: Can't distinguish natural vs. planted on its own
3. **Commission errors**: May miss sparse forests, small clearings

### Dynamic World Limitations:
1. **Short time series**: Only 2016-present
2. **Includes all trees**: Coffee estates, urban parks counted as "tree" class
3. **Probability-based**: Need to choose threshold (we use >0.5)

### Western Ghats Specific Challenges:
1. **Coffee agroforestry**: Shade-grown coffee under native tree canopy (natural or plantation?)
2. **Sacred groves**: Small old-growth patches in agricultural matrix
3. **Cardamom plantations**: Under forest canopy, hard to detect from space
4. **Teak/Eucalyptus**: Large-scale plantations, easier to identify
5. **Monsoon clouds**: Persistent cloud cover limits satellite observations

---

## ✅ Next Steps: Corrected Analysis

To fix the analysis, we need to:

### 1. **Re-run with correct probability threshold**
- Change `natural_forest_2020.eq(1)` to `.gte(130)`
- This will capture ALL natural forests >= 52% probability

### 2. **Create confidence-stratified outputs**
- High confidence (>80%): `.gte(200)`
- Medium confidence (52-80%): `.gte(130).and(.lt(200))`
- Low confidence (40-52%): `.gte(100).and(.lt(130))`

### 3. **Validate with other datasets**
- Cross-check with Hansen 2000 tree cover
- Compare with GLC-FCS30D historical forest classes
- Verify against known protected areas (should be mostly natural)

### 4. **District-level corrected statistics**
- Re-calculate natural vs. plantation ratios
- Identify districts with highest natural forest loss
- Find plantation expansion hotspots

### 5. **Temporal analysis**
- Use Hansen lossyear to track when natural forests were lost
- Use Hansen gain to identify when plantations were established
- Create 1987-2025 timeline of forest type changes

---

## 🎓 Key Takeaways

1. **Always check dataset documentation** for proper usage (probability thresholds!)
2. **Nature-Trace is probabilistic**, not binary - must use appropriate threshold
3. **Old-growth ⊂ Natural forest** - old-growth is highest integrity subset
4. **Multi-source validation** is critical for forest type classification
5. **Western Ghats complexity** requires careful interpretation (agroforestry, sacred groves)
6. **The current outputs are UNRELIABLE** and need to be regenerated with corrected methodology

**Bottom line:** We need to re-run the entire analysis with the correct probability threshold (>= 130) to get meaningful results about natural forests vs. plantations in the Western Ghats.
