import json
import re
from datetime import datetime
from itertools import groupby


def read_json(file_path='a:\git_status.json'):
    with open(file_path, 'r', encoding='utf-8') as fi:
        return json.load(fi)


def parse_branches(json_data):
    re_branch = re.compile(r'^.*(?P<hash>[0-9a-f]{6,}) (?P<datetime>\d\d-\d\d-\d\d \d\d:\d\d) \[.+]\ (?P<commit>.*$)')

    for repo in json_data:
        # remove redundant branches, favor remote branches which have been updated by a fetch
        remote_branches = set([b.split('/')[-1] for b in repo['branches'].keys() if b[:8] != 'remotes/'])
        branches = {k: v for k, v in repo['branches'].items() if k[:8] == 'remotes/' or k not in remote_branches}
        parsed_branches = {}
        # parse commits
        repo['parsed_branches'] = {
            branch.split('/')[-1]:
                [{k: datetime.strptime(v, '%y-%m-%d %H:%M') if k == 'datetime' else v
                  for k, v in ma.groupdict().items()}
                 for ma in [re_branch.match(c) for c in commits] if ma is not None]
            for branch, commits in branches.items()
        }
        repo['profile'] = {k: len(list(v)) for k, v in groupby([v for b in repo['parsed_branches'].values() for v in b],
                                                               lambda x: x['datetime'].strftime('%Y-%m'))}
        repo['folder_name'] = repo['folder'].split('\\')[-1]
        repo['name'] = (repo['remote'].replace('/ (push)', '').split('/')[-1].replace('(push)', '').strip()
                        if repo['remote'] and isinstance(repo['remote'], str)
                        else repo['remote'][0].split('/')[-1].replace('(push)', '').strip()
        if repo['remote'] and isinstance(repo['remote'], list)
        else repo['folder_name'])
    return json_data


def aggregate_projects(json_data, mapping: dict):
    projects = {k: {d: sum((cc[1] for cc in c)) for d, c in groupby([i
                                                                     for profile in v
                                                                     for i in profile['profile'].items()
                                                                     ],
                                                                    lambda x: x[0])}
                for k, v in groupby(json_data, lambda x: mapping.get(x['name'], x['name']))}

    return projects


def build_md(json_data):
    dates = set((mth for repo in json_data for mth in repo['profile'].keys()))
    md = ' | ' + ' |\n| '.join([
                                   ' | '.join(['Repository', 'Folder'] + sorted(dates)),
                                   ' | '.join(['---'] * (len(dates) + 2))
                               ]
                               + [
                                   ' | '.join(
                                       [repo['name'], repo['folder_name']] + [str(repo['profile'].get(mth, '')) for mth
                                                                              in dates])
                                   for repo in sorted(json_data, key=lambda x: x['name'])])

    return md


# build stats

data = parse_branches(read_json())
dumps = json.dumps(data, indent=2, default=str)
with open('a:\git_status_parsed.json', 'w', encoding='utf-8') as fo:
    fo.write(dumps)
print(dumps)

with open('a:\git_status_parsed.md', 'w', encoding='utf-8') as fo:
    fo.write(build_md(data))

mapping = {
    "A1.git"                                                  : "A1.git",
    "Affinity2.0"                                             : "Affinity2.0",
    "AwsSqsTest.git"                                          : "AwsSqsTest.git",
    "CmdlineConfigParser"                                     : "CmdlineConfigParser",
    "ColoredTail.git"                                         : "ColoredTail.git",
    "CommodityXL.BatchProcesses"                              : "CommodityXL.BatchProcesses",
    "CommodityXL.CxlOptionVolMarksTransformer"                : "CommodityXL.CxlOptionVolMarksTransformer",
    "CommodityXL.GenericToolboxAddin"                         : "CommodityXL.GenericToolboxAddin",
    "CommodityXL.GenericToolboxService"                       : "CommodityXL.GenericToolboxService",
    "CommodityXL.GlobalGasOptimization"                       : "CommodityXL.GlobalGasOptimization",
    "CommodityXL.GlobalGasOptimizationAddin"                  : "CommodityXL.GlobalGasOptimizationAddin",
    "CommodityXL.GlobalGasOptimizationAddin2"                 : "CommodityXL.GlobalGasOptimizationAddin2",
    "CommodityXL.IntegrationPriceSnap"                        : "CommodityXL.IntegrationPriceSnap",
    "CommodityXL.NominationActualsLoader"                     : "CommodityXL.NominationActualsLoader",
    "CommodityXL.NominationClensLoader"                       : "CommodityXL.NominationClensLoader",
    "CommodityXL.PowerStrategiesBalancing"                    : "CommodityXL.PowerStrategiesBalancing",
    "CommodityXL.PricingInterface"                            : "CommodityXL.PricingInterface",
    "CommodityXL.ServiceBridge"                               : "CommodityXL.ServiceBridge",
    "CommodityXL.StorageOptimisation.Cloud"                   : "CommodityXL.StorageOptimisation.Cloud",
    "CommodityXL.TradeReconciliation.Barclays"                : "CommodityXL.TradeReconciliation.Barclays",
    "CommodityXL.TradeReconciliation.FXAll"                   : "CommodityXL.TradeReconciliation.FXAll",
    "CommodityXL.TradeTransformers.Core"                      : "CommodityXL.TradeTransformers.Core",
    "CommodityXL.TradeTransformers.EPEX"                      : "CommodityXL.TradeTransformers.EPEX",
    "CommodityXL.TradeTransformers.FXALL"                     : "CommodityXL.TradeTransformers.FXALL",
    "CommodityXL.TradeTransformers.ICE"                       : "CommodityXL.TradeTransformers.ICE",
    "CommodityXL.TradeTransformers.KstAffinityDataService"    : "CommodityXL.TradeTransformers.KstAffinityDataService",
    "CommodityXL.TradeTransformers.TradeLoaderSVC"            : "CommodityXL.TradeTransformers.TradeLoaderSVC",
    "CommodityXL.TradeTransformers.TradeLoaderSqlScripts"     : "CommodityXL.TradeTransformers.TradeLoaderSqlScripts",
    "CommodityXL.TradeTransformers.Trayport"                  : "CommodityXL.TradeTransformers.Trayport",
    "CommodityXLClient"                                       : "CommodityXLClient",
    "CommodityXl.APIBridges.EODBatchService"                  : "CommodityXl.APIBridges.EODBatchService",
    "CommodityXl.APIBridges.MarketDataService"                : "CommodityXl.APIBridges.MarketDataService",
    "CommodityXl.APIBridges.TradesService"                    : "CommodityXl.APIBridges.TradesService",
    "CommodityXl.Power.Nominations.GMSL"                      : "CommodityXl.Power.Nominations.GMSL",
    "ConsoleApp1"                                             : "ConsoleApp1",
    "ConsoleApp2"                                             : "ConsoleApp2",
    "ConsoleApp3"                                             : "ConsoleApp3",
    "ConsoleApplication1"                                     : "ConsoleApplication1",
    "ConsoleRunner.git"                                       : "ConsoleRunner.git",
    "CoreDSPerformance.git"                                   : "CoreDSPerformance.git",
    "Database.KST_ENT"                                        : "Database.KST_ENT",
    "DnaThreadingIssue.git"                                   : "DnaThreadingIssue.git",
    "EncodeBase.git"                                          : "EncodeBase.git",
    "FAC.facConsumeEodManifest"                               : "FAC.facConsumeEodManifest",
    "FAC.facEntityFlattener"                                  : "FAC.facEntityFlattener",
    "FAC.facEodStartAndSnap"                                  : "FAC.facEodStartAndSnap",
    "FAC.facProcessEodManifest"                               : "FAC.facProcessEodManifest",
    "FAC.loaderCashflowFromQueue"                             : "FAC.loaderCashflowFromQueue",
    "FAC.positionEod"                                         : "FAC.positionEod",
    "FHR.CoreDs.DataSnapper"                                  : "FHR.CoreDs.DataSnapper",
    "GENSCAPE_OIL_INTELLIGENCE"                               : "GENSCAPE_OIL_INTELLIGENCE",
    "GetWindowsAccessToken"                                   : "GetWindowsAccessToken",
    "GlobalGas.CurveBuilder"                                  : "GlobalGas.CurveBuilder",
    "GlobalGas.PowerOption.Excel.Addin"                       : "GlobalGas.PowerOption.Excel.Addin",
    "GlobalGasAnalytics"                                      : "GlobalGasAnalytics",
    "GmeNatGasExchangeMonitor"                                : "GmeNatGasExchangeMonitor",
    "Gundies"                                                 : "Gundies",
    "Gundies.ExcelAddIn"                                      : "Gundies.ExcelAddIn",
    "GundiesWebLogs"                                          : "GundiesWebLogs",
    "ITTools.JobTrigger"                                      : "ITTools.JobTrigger",
    "ITTools.KSTMigration"                                    : "ITTools.KSTMigration",
    "ITTools.MigrationHelpers"                                : "ITTools.MigrationHelpers",
    "KST.AWS.SignatureV4"                                     : "KST.AWS.SignatureV4",
    "KST.Analytics.Trade360"                                  : "KST.Analytics.Trade360",
    "KST.Analytics.Trade360.AWSIntegration"                   : "KST.Analytics.Trade360.AWSIntegration",
    "Kst.Common.Excel"                                        : "Kst.Common.Excel",
    "KstAffinityDataService"                                  : "KstAffinityDataService",
    "KstHelpers.Nuget.Library"                                : "KstHelpers.Nuget.Library",
    "LinqPadCsvFix.git"                                       : "LinqPadCsvFix.git",
    "LinqpadQ.git"                                            : "LinqpadQ.git",
    "LogTimer.git"                                            : "LogTimer.git",
    "LyncLog"                                                 : "LyncLog",
    "MarketData"                                              : "MarketData",
    "MarketData.AppStore.Client"                              : "MarketData.AppStore.Client",
    "MarketData.AppStore.Database"                            : "MarketData.AppStore.Database",
    "MarketData.AppStore.Packager"                            : "MarketData.AppStore.Packager",
    "MarketData.AppStore.Server"                              : "MarketData.AppStore.Server",
    "MarketData.COMET"                                        : "MarketData.COMET",
    "MarketData.Common"                                       : "MarketData.Common",
    "MarketData.CoreDS.COMET"                                 : "MarketData.CoreDS.COMET",
    "MarketData.CoreDS.Calendar"                              : "MarketData.CoreDS.Calendar",
    "MarketData.CoreDS.DRM"                                   : "MarketData.CoreDS.DRM",
    "MarketData.CoreDS.DataLoad"                              : "MarketData.CoreDS.DataLoad",
    "MarketData.CoreDS.Database"                              : "MarketData.CoreDS.Database",
    "MarketData.CoreDS.DimensionParser"                       : "MarketData.CoreDS.DimensionParser",
    "MarketData.CoreDS.Distributions"                         : "MarketData.CoreDS.Distributions",
    "MarketData.CoreDS.EventPipelineFramework"                : "MarketData.CoreDS.EventPipelineFramework",
    "MarketData.CoreDS.KAdmin"                                : "MarketData.CoreDS.KAdmin",
    "MarketData.CoreDS.Messaging"                             : "MarketData.CoreDS.Messaging",
    "MarketData.CoreDS.Tagging"                               : "MarketData.CoreDS.Tagging",
    "MarketData.Freight.IMOSEstimateService"                  : "MarketData.Freight.IMOSEstimateService",
    "MarketData.Freight.MarineCurves.AmphoraEventPump"        : "MarketData.Freight.MarineCurves.AmphoraEventPump",
    "MarketData.Freight.TransportationForwardCalculator"      : "MarketData.Freight.TransportationForwardCalculator",
    "MarketData.GulpTest"                                     : "MarketData.GulpTest",
    "MarketData.Irony"                                        : "MarketData.Irony",
    "MarketData.KCalc"                                        : "MarketData.KCalc",
    "MarketData.KLiveCDC"                                     : "MarketData.KLiveCDC",
    "MarketData.KQuery"                                       : "MarketData.KQuery",
    "MarketData.KQuery.NetCore"                               : "MarketData.KQuery.NetCore",
    "MarketData.KSuite.KShare"                                : "MarketData.KSuite.KShare",
    "MarketData.KSuite.KShare.AspNetCore"                     : "MarketData.KSuite.KShare.AspNetCore",
    "MarketData.KSuite.Site"                                  : "MarketData.KSuite.Site",
    "MarketData.KstExcelAddinCommon"                          : "MarketData.KstExcelAddinCommon",
    "MarketData.MDISPlus"                                     : "MarketData.MDISPlus",
    "MarketData.MDISPlusFeeders.CME.DataMineAPI"              : "MarketData.MDISPlusFeeders.CME.DataMineAPI",
    "MarketData.ReutersDataScope.Loader"                      : "MarketData.ReutersDataScope.Loader",
    "MarketData.SDRDW"                                        : "MarketData.SDRDW",
    "MarketData.Tools"                                        : "MarketData.Tools",
    "MoreLINQ.git"                                            : "MoreLINQ.git",
    "NDate.git"                                               : "NDate.git",
    "Now.git"                                                 : "Now.git",
    "PLReporting.SSAS.Tabular"                                : "PLReporting.SSAS.Tabular",
    "PrismaTradeTransformer"                                  : "PrismaTradeTransformer",
    "PythonExploratory.git"                                   : "PythonExploratory.git",
    "Rdatasets.cs.git"                                        : "Rdatasets.cs.git",
    "ReleaseManagementSample"                                 : "ReleaseManagementSample",
    "SimpleCommandLineParser.git"                             : "SimpleCommandLineParser.git",
    "SqlObjetsRecompiler.git"                                 : "SqlObjetsRecompiler.git",
    "SqlResultComparer.git"                                   : "SqlResultComparer.git",
    "Starfish"                                                : "Starfish",
    "Strategies Dashboard"                                    : "Strategies Dashboard",
    "TestCognito.git"                                         : "TestCognito.git",
    "TptVolmarksTransformerKCalc"                             : "TptVolmarksTransformerKCalc",
    "TradeLoader.ICE.KstIceTradeLoader"                       : "TradeLoader.ICE.KstIceTradeLoader",
    "TradeLoader.PrismaParser"                                : "TradeLoader.PrismaParser",
    "TradeLoaders.Epex"                                       : "TradeLoaders.Epex",
    "TradeLoaders.Trayport"                                   : "TradeLoaders.Trayport",
    "Tradeloaders.API.CommodityXLTradesFramework"             : "Tradeloaders.API.CommodityXLTradesFramework",
    "Tradeloaders.AffinityDataService"                        : "Tradeloaders.AffinityDataService",
    "Tradeloaders.HoldingTanks.CommodityXLTrades"             : "Tradeloaders.HoldingTanks.CommodityXLTrades",
    "Tradeloaders.Transformers.CmeCxl"                        : "Tradeloaders.Transformers.CmeCxl",
    "Tradeloaders.Transformers.CmeSymphony"                   : "Tradeloaders.Transformers.CmeSymphony",
    "TrayportTrades"                                          : "TrayportTrades",
    "Trinity.BatchProcesses"                                  : "Trinity.BatchProcesses",
    "Vahana"                                                  : "Vahana",
    "Weather"                                                 : "Weather",
    "atet-api"                                                : "atet-api",
    "atet-catalog-loader"                                     : "atet-catalog-loader",
    "atet-catalog-loader.git"                                 : "atet-catalog-loader.git",
    "atet-collection-event-consumer"                          : "atet-collection-event-consumer",
    "atet-collection-poller"                                  : "atet-collection-poller",
    "atet-common-iam"                                         : "atet-common-iam",
    "atet-coreds-distribution-event-consumer"                 : "atet-coreds-distribution-event-consumer",
    "atet-drc-drm-replication"                                : "atet-drc-drm-replication",
    "atet-gundies-catalog-loader.git"                         : "atet-gundies-catalog-loader.git",
    "atet-gundies-history-load.git"                           : "atet-gundies-history-load.git",
    "atet-history-load"                                       : "atet-history-load",
    "atet-infrastructure"                                     : "atet-infrastructure",
    "atet-kcall-interceptor"                                  : "atet-kcall-interceptor",
    "atet-object-poller"                                      : "atet-object-poller",
    "atet-partition-event-consumer"                           : "atet-partition-event-consumer",
    "azure-activedirectory-library-for-python.git"            : "azure-activedirectory-library-for-python.git",
    "blpapi-python.git"                                       : "blpapi-python.git",
    "bom-vs-boy-vs-cal"                                       : "bom-vs-boy-vs-cal",
    "calendar-migration.git"                                  : "calendar-migration.git",
    "catalog-api-service.git"                                 : "catalog-api-service.git",
    "catalog-external-loader.git"                             : "catalog-external-loader.git",
    "catalog-query-api-service.git"                           : "catalog-query-api-service.git",
    "cce-coded-curves.git"                                    : "cce-coded-curves.git",
    "colonialcycleinterp.git"                                 : "colonialcycleinterp.git",
    "core-infrastructure-mongodb.git"                         : "core-infrastructure-mongodb.git",
    "coreds-event-pipeline-batch-distributor.git"             : "coreds-event-pipeline-batch-distributor.git",
    "coreds-event-pipeline-kcall-interceptor.git"             : "coreds-event-pipeline-kcall-interceptor.git",
    "coreds-event-pipeline-structure-node-consumer.git"       : "coreds-event-pipeline-structure-node-consumer.git",
    "data-pipeline-schemas.git"                               : "data-pipeline-schemas.git",
    "data-subscription-definitions.git"                       : "data-subscription-definitions.git",
    "dataframe-engine-service.git"                            : "dataframe-engine-service.git",
    "datasnapper.git"                                         : "datasnapper.git",
    "distribution-check-conti"                                : "distribution-check-conti",
    "distribution-manager-service.git"                        : "distribution-manager-service.git",
    "distributions-manager-service-deployment.git"            : "distributions-manager-service-deployment.git",
    "distributions-work-dispatcher-service.git"               : "distributions-work-dispatcher-service.git",
    "dockerawspythonexplore.git"                              : "dockerawspythonexplore.git",
    "drc-evaluation-api-service.git"                          : "drc-evaluation-api-service.git",
    "drc-ui-api-service.git"                                  : "drc-ui-api-service.git",
    "drm-coreds-database-changes"                             : "drm-coreds-database-changes",
    "drm-drc-migration"                                       : "drm-drc-migration",
    "eu-td-aggregator"                                        : "eu-td-aggregator",
    "eu-wind-aggregator"                                      : "eu-wind-aggregator",
    "eua-switch-prices"                                       : "eua-switch-prices",
    "european-black-scholes-76-xll.git"                       : "european-black-scholes-76-xll.git",
    "european-black-scholes-76.git"                           : "european-black-scholes-76.git",
    "front-month-analysis"                                    : "front-month-analysis",
    "front-week-analysis"                                     : "front-week-analysis",
    "gas-level-overview"                                      : "gas-level-overview",
    "gas-storage-gse"                                         : "gas-storage-gse",
    "generic-stack"                                           : "generic-stack",
    "git-commands.git"                                        : "git-commands.git",
    "gundies-to-ksuite-data-service.git"                      : "gundies-to-ksuite-data-service.git",
    "gundies-to-ksuite-data-service.wiki.git"                 : "gundies-to-ksuite-data-service.wiki.git",
    "iam-roles.git"                                           : "iam-roles.git",
    "kcalc-api-service-3-deployment.git"                      : "kcalc-api-service-3-deployment.git",
    "kcalc-api-service-3.git"                                 : "kcalc-api-service-3.git",
    "kcalc-calculation-dispatcher"                            : "kcalc-calculation-dispatcher",
    "kcalc-calculation-dispatcher-3-deployment.git"           : "kcalc-calculation-dispatcher-3-deployment.git",
    "kcalc-calculation-dispatcher-3.git"                      : "kcalc-calculation-dispatcher-3.git",
    "kcalc-calculation-dispatcher.git"                        : "kcalc-calculation-dispatcher.git",
    "kcalc-calculation-manager-3-deployment.git"              : "kcalc-calculation-manager-3-deployment.git",
    "kcalc-calculation-manager-3.git"                         : "kcalc-calculation-manager-3.git",
    "kcalc-calculation-manager.git"                           : "kcalc-calculation-manager.git",
    "kcalc-cli-integration-tests.git"                         : "kcalc-cli-integration-tests.git",
    "kcalc-coded-curves.git"                                  : "kcalc-coded-curves.git",
    "kcalc-core"                                              : "kcalc-core",
    "kcalc-coreds-legacy-event-pump"                          : "kcalc-coreds-legacy-event-pump",
    "kcalc-coreds-legacy-event-pump.git"                      : "kcalc-coreds-legacy-event-pump.git",
    "kcalc-custom-code-runner-deployment.git"                 : "kcalc-custom-code-runner-deployment.git",
    "kcalc-custom-code-runner.git"                            : "kcalc-custom-code-runner.git",
    "kcalc-data-model-3.git"                                  : "kcalc-data-model-3.git",
    "kcalc-dependency-evaluator"                              : "kcalc-dependency-evaluator",
    "kcalc-engine-infrastructure.git"                         : "kcalc-engine-infrastructure.git",
    "kcalc-infrastructure.git"                                : "kcalc-infrastructure.git",
    "kcalc-kquery-api-gateway"                                : "kcalc-kquery-api-gateway",
    "kcalc-kquery-bridge"                                     : "kcalc-kquery-bridge",
    "kcalc-module-options-volatility.git"                     : "kcalc-module-options-volatility.git",
    "kcalc-modules-3.git"                                     : "kcalc-modules-3.git",
    "kcalc-modules.git"                                       : "kcalc-modules.git",
    "kcalc-published-curves-service.git"                      : "kcalc-published-curves-service.git",
    "kcalc-python-coded-curve-workbench.git"                  : "kcalc-python-coded-curve-workbench.git",
    "kcalc-result-legacy-loader.git"                          : "kcalc-result-legacy-loader.git",
    "kcalc-test-helper.git"                                   : "kcalc-test-helper.git",
    "kcalc-ui-api-service.git"                                : "kcalc-ui-api-service.git",
    "kcalc-ui.git"                                            : "kcalc-ui.git",
    "kcalc-user-settings-service.git"                         : "kcalc-user-settings-service.git",
    "kcalc-workspace-service.git"                             : "kcalc-workspace-service.git",
    "kcalc3-utilities.git"                                    : "kcalc3-utilities.git",
    "kochid-cli.git"                                          : "kochid-cli.git",
    "kquery-api-service.git"                                  : "kquery-api-service.git",
    "kquery-api.git"                                          : "kquery-api.git",
    "kquery-core.git"                                         : "kquery-core.git",
    "kquery-core.wiki.git"                                    : "kquery-core.wiki.git",
    "kquery-engine-service.git"                               : "kquery-engine-service.git",
    "kquery-excel-addin.git"                                  : "kquery-excel-addin.git",
    "kquery-gui-api.git"                                      : "kquery-gui-api.git",
    "kquery-single-series"                                    : "kquery-single-series",
    "kquery-test-data.git"                                    : "kquery-test-data.git",
    "kquery-ui-api-service.git"                               : "kquery-ui-api-service.git",
    "ksuite-cli.git"                                          : "ksuite-cli.git",
    "ksuite-cloud-docs"                                       : "ksuite-cloud-docs",
    "ksuite-cloud-planning.wiki.git"                          : "ksuite-cloud-planning.wiki.git",
    "ksuite-datastore-controller.git"                         : "ksuite-datastore-controller.git",
    "ksuite-lambda-app.git"                                   : "ksuite-lambda-app.git",
    "ksuite-period-codes.git"                                 : "ksuite-period-codes.git",
    "ksuite-structure-data-pipeline"                          : "ksuite-structure-data-pipeline",
    "ksuitedotnet.git"                                        : "ksuitedotnet.git",
    "ksuitepy.git"                                            : "ksuitepy.git",
    "live-dashboard.git"                                      : "live-dashboard.git",
    "live-positions.git"                                      : "live-positions.git",
    "lng-fundamentals.git"                                    : "lng-fundamentals.git",
    "lng-marking.git"                                         : "lng-marking.git",
    "lng-prices.git"                                          : "lng-prices.git",
    "lng-terminal-tracker.git"                                : "lng-terminal-tracker.git",
    "lng-terminals.git"                                       : "lng-terminals.git",
    "lng-yoy-report.git"                                      : "lng-yoy-report.git",
    "morning-prompt-analysis"                                 : "morning-prompt-analysis",
    "nelder-mead-simplex.git"                                 : "nelder-mead-simplex.git",
    "ngbasisplusdiff.git"                                     : "ngbasisplusdiff.git",
    "options-package-validation.git"                          : "options-package-validation.git",
    "pricing-xl-add-in.git"                                   : "pricing-xl-add-in.git",
    "pwr-prompt-dashboard"                                    : "pwr-prompt-dashboard",
    "pwr-prompt-thermal-demand"                               : "pwr-prompt-thermal-demand",
    "pwr-st-stack-model"                                      : "pwr-st-stack-model",
    "py_vollib.git"                                           : "py_vollib.git",
    "pycurvebuilder.git"                                      : "pycurvebuilder.git",
    "pyhellotest.git"                                         : "pyhellotest.git",
    "python3-connect-rest-sample.git"                         : "python3-connect-rest-sample.git",
    "pythonexploratory.git"                                   : "pythonexploratory.git",
    "r-install.ps.git"                                        : "r-install.ps.git",
    "run-pwr-dashboards-am"                                   : "run-pwr-dashboards-am",
    "sandboxing.git"                                          : "sandboxing.git",
    "schema-definitions.git"                                  : "schema-definitions.git",
    "secrets.ps.git"                                          : "secrets.ps.git",
    "smop.git"                                                : "smop.git",
    "sparks-and-darks-lp"                                     : "sparks-and-darks-lp",
    "starfish-cxl-sql.git"                                    : "starfish-cxl-sql.git",
    "storage-levels.git"                                      : "storage-levels.git",
    "storageoptimizationaddin.git"                            : "storageoptimizationaddin.git",
    "structure-api-service-deployment.git"                    : "structure-api-service-deployment.git",
    "structure-api-service.git"                               : "structure-api-service.git",
    "structure-data-pipeline-async-consumer.git"              : "structure-data-pipeline-async-consumer.git",
    "structure-data-pipeline-service.git"                     : "structure-data-pipeline-service.git",
    "structure-data-pipeline-workflow-manager.git"            : "structure-data-pipeline-workflow-manager.git",
    "structure-datastore-controller-daterange-partitioner.git": "structure-datastore-controller-daterange-partitioner.git",
    "structure-datastore-controller-single-partitioner.git"   : "structure-datastore-controller-single-partitioner.git",
    "structure-datastore-events-publisher.git"                : "structure-datastore-events-publisher.git",
    "subscription_service.git"                                : "subscription_service.git",
    "tpt-options-pricing.git"                                 : "tpt-options-pricing.git",
    "transportation-forward.git"                              : "transportation-forward.git",
    "wkday-wkend-base-peak"                                   : "wkday-wkend-base-peak"
}

aggregated = aggregate_projects(data, mapping)
with open('a:\git_status_aggregated.json', 'w', encoding='utf-8') as fo:
    fo.write(json.dumps(aggregated, indent=2, default=str))

print(json.dumps({k: k for k in sorted((k for k in aggregated.keys()))}, indent=2, default=str))
