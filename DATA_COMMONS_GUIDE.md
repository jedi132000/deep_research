# 🌍 Data Commons Integration Guide

## What is Data Commons?

Google's **Data Commons** is a vast repository of public statistical data that includes:

- **📊 Economic indicators**: GDP, unemployment, inflation, trade data
- **👥 Demographics**: Population, age distributions, education levels
- **🏥 Health statistics**: Disease prevalence, mortality rates, healthcare access
- **🌍 Environmental data**: Climate, pollution levels, energy consumption  
- **🏛 Social indicators**: Crime rates, housing data, transportation statistics
- **🌾 Agricultural data**: Crop yields, food security, farming statistics

The Enhanced MCP Research mode gives you programmatic access to this treasure trove of verified public data.

## 🚀 Quick Setup

### 1. Get Your Free API Key

1. Visit **[apikeys.datacommons.org](https://apikeys.datacommons.org/)**
2. Request an API key for the `api.datacommons.org` domain
3. It's completely **free** for research and development use

### 2. Configure Your Environment

Add your API key to your `.env` file:

```bash
# Add this line to your .env file
DC_API_KEY=your_data_commons_api_key_here
```

### 3. Install Enhanced Dependencies

```bash
# Install the enhanced MCP dependencies
pip install -e ".[enhanced]"

# Or install Data Commons separately
pip install datacommons-mcp
```

## 🔍 Example Queries

### Economic Analysis
```bash
deep-research -m enhanced -q "Compare GDP growth rates for G7 countries over the last decade"

deep-research -m enhanced -q "Analyze unemployment trends in European Union countries"

deep-research -m enhanced -q "Generate a report on inflation rates vs wage growth in developing nations"
```

### Health & Demographics  
```bash
deep-research -m enhanced -q "Compare life expectancy across different US states and identify key factors"

deep-research -m enhanced -q "Analyze the relationship between education levels and health outcomes globally"

deep-research -m enhanced -q "What are the demographic trends in aging populations worldwide?"
```

### Environmental Research
```bash
deep-research -m enhanced -q "Compare carbon emissions per capita across major economies"

deep-research -m enhanced -q "Analyze renewable energy adoption trends by country and region"

deep-research -m enhanced -q "How do climate indicators correlate with economic development?"
```

### Social & Policy Research
```bash  
deep-research -m enhanced -q "Examine the relationship between income inequality and social mobility"

deep-research -m enhanced -q "Compare healthcare spending efficiency across different countries"

deep-research -m enhanced -q "Analyze urban population growth and infrastructure development patterns"
```

## 🛠 Advanced Usage

### Combining Local Data with Statistics

The enhanced mode is perfect for research that needs both local context and public statistics:

```bash
# Analyze your local business data against national economic trends
deep-research -m enhanced -q "Compare our local sales data with national retail trends and economic indicators"

# Academic research combining literature review with statistical analysis
deep-research -m enhanced -q "Synthesize findings from local research papers with national health statistics"
```

### Web Interface

The enhanced mode is also available in the web interface:

1. Run `streamlit run web_app.py`
2. Select **"Enhanced MCP Research"** from the mode options
3. Enter queries that benefit from statistical data

## 🎯 Best Practices

### Effective Query Patterns

✅ **Good queries:**
- "Compare [metric] across [geographic regions/countries]"
- "Analyze the relationship between [variable A] and [variable B]"
- "Generate a report on [topic] using statistical data"
- "What are the trends in [indicator] over [time period]?"

❌ **Less effective:**
- Very general queries without specific metrics
- Questions about recent events (data may have delays)
- Requests for opinion-based analysis (stick to statistical facts)

### Combining with Other Modes

- Use **Basic Research** for current events and recent developments
- Use **Enhanced MCP** for statistical analysis and historical trends  
- Use **MCP Research** for local document analysis
- Use **Full Multi-Agent** for complex multi-faceted research

## 🔧 Troubleshooting

### API Key Issues
```bash
# Check if your API key is loaded
echo $DC_API_KEY

# Verify your .env file contains the key
grep DC_API_KEY .env
```

### Fallback Behavior
If the Data Commons API key isn't configured, the enhanced mode automatically falls back to filesystem-only MCP research.

### Rate Limits
Data Commons has generous rate limits for research use. If you hit limits, queries will be throttled automatically.

## 🤝 Contributing

Found interesting patterns in your research? Consider:
- Sharing example queries that worked well
- Reporting any data quality issues to Google Data Commons
- Suggesting improvements to the MCP integration

## 📚 Additional Resources

- **[Data Commons Documentation](https://docs.datacommons.org/)**
- **[API Reference](https://docs.datacommons.org/api/)**
- **[Data Sources](https://datacommons.org/datasets)**
- **[MCP Protocol Specification](https://modelcontextprotocol.io/)**

---

**Ready to explore the world's data?** Start with:
```bash
deep-research -m enhanced -q "What health data do you have for Africa?"
```