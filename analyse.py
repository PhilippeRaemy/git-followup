import json
import re
from datetime import datetime
from itertools import groupby
from typing import Callable


def read_json(file_path='a:\git_status\git_status.json'):
    with open(file_path, 'r', encoding='utf-8') as fi:
        return json.load(fi)


def parse_branches(json_data, period_aggregator: Callable):
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
        repo['profile'] = {k: len(list(v)) for k, v in groupby(
            sorted([v for b in repo['parsed_branches'].values() for v in b], key=period_aggregator),
            period_aggregator)}
        repo['folder_name'] = repo['folder'].split('\\')[-1]
        repo['name'] = (repo['remote'].replace('/ (push)', '').split('/')[-1].replace('(push)', '').strip()
                        if repo['remote'] and isinstance(repo['remote'], str)
                        else repo['remote'][0].split('/')[-1].replace('(push)', '').strip()
        if repo['remote'] and isinstance(repo['remote'], list)
        else repo['folder_name'])
    return json_data


# (groupby(sorted(((j, mapping.get(j['name'], j['name'])) for j in json_data), key=lambda j:j[1]) , lambda x:x[1]))
# list(groupby(sorted(((j, mapping.get(j['name'], j['name'])) for j in json_data), key=lambda j:j[1]) , lambda x:x[1]))
# list((k, [vv[0] for vv in v]) for k, v in groupby(sorted(((j, mapping.get(j['name'], j['name']).capitalize()) for j in json_data), key=lambda j:j[1]) , lambda x:x[1]))

def aggregate_projects(json_data, mapping: dict):
    projects = {k: v
                for k, v
                in sorted(((k,
                            {d: sum((cc[1] for cc in c))
                             for d, c in groupby([i for profile in v
                                                  for i in profile['profile'].items()],
                                                 lambda x: x[0])})
                           for k, v in ((k, [vv[0] for vv in v]) for k, v in groupby(
            sorted(((j, mapping.get(j['name'], j['name']).capitalize()) for j in json_data), key=lambda j: j[1]),
            lambda x: x[1]))),
                          key=lambda x: x[0])
                if v}

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


def build_md_from_agged(json_data):
    dates = set((mth for repo in json_data.values() for mth in repo.keys()))
    md = ' | ' + ' |\n| '.join([
                                   ' | '.join(['Repository'] + sorted(dates)),
                                   ' | '.join(['---'] * (len(dates) + 1))
                               ]
                               + [
                                   ' | '.join(
                                       [k] + [str(v.get(mth, '')) for mth in dates])
                                   for k, v in json_data.items()])

    return md


# build stats

month_aggregator = lambda x: x['datetime'].strftime('%Y-%m')
quarter_aggregator = lambda x: x['datetime'].strftime('%Y') + 'Q' + str((x['datetime'].month - 1) // 3 + 1)
year_aggregator = lambda x: x['datetime'].strftime('%Y')

data = parse_branches(read_json(), year_aggregator)
dumps = json.dumps(data, indent=2, default=str)
with open('a:\git_status\git_status_parsed.json', 'w', encoding='utf-8') as fo:
    fo.write(dumps)
print(dumps)

with open('a:\git_status\git_status_parsed.md', 'w', encoding='utf-8') as fo:
    fo.write(build_md(data))

mapping = {
    "A1.git"                                                  : "Scratches",
    "Affinity2.0"                                             : "Affinity",
    "AwsSqsTest.git"                                          : "Scratches",
    "CmdlineConfigParser"                                     : "CmdlineConfigParser",
    "ColoredTail.git"                                         : "Tools",
    "CommodityXL.BatchProcesses"                              : "CXL",
    "CommodityXL.CxlOptionVolMarksTransformer"                : "CXL.CxlOptionVolMarksTransformer",
    "CommodityXL.GenericToolboxAddin"                         : "CXL.GenericToolbox",
    "CommodityXL.GenericToolboxService"                       : "CXL.GenericToolbox",
    "CommodityXL.GlobalGasOptimization"                       : "CXL.GlobalGasOptimization",
    "CommodityXL.GlobalGasOptimizationAddin"                  : "CXL.GlobalGasOptimization",
    "CommodityXL.GlobalGasOptimizationAddin2"                 : "CXL.GlobalGasOptimization",
    "CommodityXL.IntegrationPriceSnap"                        : "CXL.IntegrationPriceSnap",
    "CommodityXL.NominationActualsLoader"                     : "CXL.NominationActualsLoader",
    "CommodityXL.NominationClensLoader"                       : "CXL.NominationClensLoader",
    "CommodityXL.PowerStrategiesBalancing"                    : "CXL.PowerStrategiesBalancing",
    "CommodityXL.PricingInterface"                            : "CXL",
    "CommodityXL.ServiceBridge"                               : "CXL",
    "CommodityXL.StorageOptimisation.Cloud"                   : "CXL.GlobalGasOptimization",
    "CommodityXL.TradeReconciliation.Barclays"                : "CXL.TradeReconciliation",
    "CommodityXL.TradeReconciliation.FXAll"                   : "CXL.TradeReconciliation",
    "CommodityXL.TradeTransformers.Core"                      : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.EPEX"                      : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.FXALL"                     : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.ICE"                       : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.KstAffinityDataService"    : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.TradeLoaderSVC"            : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.TradeLoaderSqlScripts"     : "CXL.TradeLoaders",
    "CommodityXL.TradeTransformers.Trayport"                  : "CXL.TradeLoaders",
    "CommodityXLClient"                                       : "CXLClient",
    "CommodityXl.APIBridges.EODBatchService"                  : "CXL.APIBridges",
    "CommodityXl.APIBridges.MarketDataService"                : "CXL.APIBridges",
    "CommodityXl.APIBridges.TradesService"                    : "CXL.APIBridges",
    "CommodityXl.Power.Nominations.GMSL"                      : "CXL.Power.Nominations.GMSL",
    "ConsoleApp1"                                             : "Scratches",
    "ConsoleApp2"                                             : "Scratches",
    "ConsoleApp3"                                             : "Scratches",
    "ConsoleApplication1"                                     : "Scratches",
    "ConsoleRunner.git"                                       : "Scratches",
    "CoreDSPerformance.git"                                   : "MarketData (legacy)",
    "Database.KST_ENT"                                        : "Affinity",
    "DnaThreadingIssue.git"                                   : "CXL.GlobalGasOptimization",
    "EncodeBase.git"                                          : "Tools",
    "FAC.facConsumeEodManifest"                               : "FAC",
    "FAC.facEntityFlattener"                                  : "FAC",
    "FAC.facEodStartAndSnap"                                  : "FAC",
    "FAC.facProcessEodManifest"                               : "FAC",
    "FAC.loaderCashflowFromQueue"                             : "FAC",
    "FAC.positionEod"                                         : "FAC",
    "FHR.CoreDs.DataSnapper"                                  : "MarketData (legacy)",
    "GENSCAPE_OIL_INTELLIGENCE"                               : "Gundies",
    "GetWindowsAccessToken"                                   : "Tools",
    "GlobalGas.CurveBuilder"                                  : "GlobalGas.CurveBuilder",
    "GlobalGas.PowerOption.Excel.Addin"                       : "GlobalGas.PowerOption.Excel.Addin",
    "GlobalGasAnalytics"                                      : "GlobalGasAnalytics (Matlab)",
    "GmeNatGasExchangeMonitor"                                : "GmeNatGasExchangeMonitor",
    "Gundies"                                                 : "Gundies",
    "Gundies.ExcelAddIn"                                      : "Gundies",
    "GundiesWebLogs"                                          : "Gundies",
    "ITTools.JobTrigger"                                      : "CXL.GlobalGasOptimization",
    "ITTools.KSTMigration"                                    : "Tools",
    "ITTools.MigrationHelpers"                                : "Tools",
    "KST.AWS.SignatureV4"                                     : "Tools",
    "KST.Analytics.Trade360"                                  : "Trade360",
    "KST.Analytics.Trade360.AWSIntegration"                   : "Trade360",
    "Kst.Common.Excel"                                        : "Tools",
    "KstAffinityDataService"                                  : "Affinity",
    "KstHelpers.Nuget.Library"                                : "Tools",
    "LinqPadCsvFix.git"                                       : "Gundies",
    "LinqpadQ.git"                                            : "Gundies",
    "LogTimer.git"                                            : "Tools",
    "LyncLog"                                                 : "Tools",
    "MarketData"                                              : "Gundies",
    "MarketData.AppStore.Client"                              : "MarketData.AppStore",
    "MarketData.AppStore.Database"                            : "MarketData.AppStore",
    "MarketData.AppStore.Packager"                            : "MarketData.AppStore",
    "MarketData.AppStore.Server"                              : "MarketData.AppStore",
    "MarketData.COMET"                                        : "MarketData (legacy)",
    "MarketData.Common"                                       : "MarketData (legacy)",
    "MarketData.CoreDS.COMET"                                 : "MarketData (legacy)",
    "MarketData.CoreDS.Calendar"                              : "MarketData (legacy)",
    "MarketData.CoreDS.DRM"                                   : "MarketData (legacy)",
    "MarketData.CoreDS.DataLoad"                              : "MarketData (legacy)",
    "MarketData.CoreDS.Database"                              : "MarketData (legacy)",
    "MarketData.CoreDS.DimensionParser"                       : "MarketData (legacy)",
    "MarketData.CoreDS.Distributions"                         : "MarketData (legacy)",
    "MarketData.CoreDS.EventPipelineFramework"                : "MarketData (legacy)",
    "MarketData.CoreDS.KAdmin"                                : "MarketData (legacy)",
    "MarketData.CoreDS.Messaging"                             : "MarketData (legacy)",
    "MarketData.CoreDS.Tagging"                               : "MarketData (legacy)",
    "MarketData.Freight.IMOSEstimateService"                  : "MarketData (legacy)",
    "MarketData.Freight.MarineCurves.AmphoraEventPump"        : "MarketData (legacy)",
    "MarketData.Freight.TransportationForwardCalculator"      : "MarketData (legacy)",
    "MarketData.GulpTest"                                     : "MarketData (legacy)",
    "MarketData.Irony"                                        : "MarketData (legacy)",
    "MarketData.KCalc"                                        : "MarketData (legacy)",
    "MarketData.KLiveCDC"                                     : "MarketData (legacy)",
    "MarketData.KQuery"                                       : "MarketData (legacy)",
    "MarketData.KQuery.NetCore"                               : "MarketData (legacy)",
    "MarketData.KSuite.KShare"                                : "MarketData (legacy)",
    "MarketData.KSuite.KShare.AspNetCore"                     : "MarketData (legacy)",
    "MarketData.KSuite.Site"                                  : "MarketData (legacy)",
    "MarketData.KstExcelAddinCommon"                          : "MarketData (legacy)",
    "MarketData.MDISPlus"                                     : "MarketData (legacy)",
    "MarketData.MDISPlusFeeders.CME.DataMineAPI"              : "MarketData (legacy)",
    "MarketData.ReutersDataScope.Loader"                      : "MarketData (legacy)",
    "MarketData.SDRDW"                                        : "MarketData (legacy)",
    "MarketData.Tools"                                        : "MarketData (legacy)",
    "MoreLINQ.git"                                            : "Gundies",
    "NDate.git"                                               : "Scratches",
    "Now.git"                                                 : "Scratches",
    "PLReporting.SSAS.Tabular"                                : "GlobalGas",
    "PrismaTradeTransformer"                                  : "CXL.TradeLoaders",
    "PythonExploratory.git"                                   : "Scratches",
    "Rdatasets.cs.git"                                        : "MarketData (legacy)",
    "ReleaseManagementSample"                                 : "Scratches",
    "SimpleCommandLineParser.git"                             : "Tools",
    "SqlObjetsRecompiler.git"                                 : "Tools",
    "SqlResultComparer.git"                                   : "Tools",
    "Starfish"                                                : "Gundies",
    "Strategies Dashboard"                                    : "Strategies Dashboard",
    "TestCognito.git"                                         : "Scratches",
    "TptVolmarksTransformerKCalc"                             : "CXL.CxlOptionVolMarksTransformer",
    "TradeLoader.ICE.KstIceTradeLoader"                       : "CXL.TradeLoaders",
    "TradeLoader.PrismaParser"                                : "CXL.TradeLoaders",
    "TradeLoaders.Epex"                                       : "CXL.TradeLoaders",
    "TradeLoaders.Trayport"                                   : "CXL.TradeLoaders",
    "Tradeloaders.API.CommodityXLTradesFramework"             : "CXL.TradeLoaders",
    "Tradeloaders.AffinityDataService"                        : "CXL.TradeLoaders",
    "Tradeloaders.HoldingTanks.CommodityXLTrades"             : "CXL.TradeLoaders",
    "Tradeloaders.Transformers.CmeCxl"                        : "CXL.TradeLoaders",
    "Tradeloaders.Transformers.CmeSymphony"                   : "CXL.TradeLoaders",
    "TrayportTrades"                                          : "CXL.TradeLoaders",
    "Trinity.BatchProcesses"                                  : "Trinity",
    "Vahana"                                                  : "GlobalGas",
    "Weather"                                                 : "Gundies",
    "atet-api"                                                : "KSuite",
    "atet-catalog-loader"                                     : "KSuite",
    "atet-catalog-loader.git"                                 : "KSuite",
    "atet-collection-event-consumer"                          : "KSuite",
    "atet-collection-poller"                                  : "KSuite",
    "atet-common-iam"                                         : "KSuite",
    "atet-coreds-distribution-event-consumer"                 : "KSuite",
    "atet-drc-drm-replication"                                : "KSuite",
    "atet-gundies-catalog-loader.git"                         : "KSuite",
    "atet-gundies-history-load.git"                           : "KSuite",
    "atet-history-load"                                       : "KSuite",
    "atet-infrastructure"                                     : "KSuite",
    "atet-kcall-interceptor"                                  : "KSuite",
    "atet-object-poller"                                      : "KSuite",
    "atet-partition-event-consumer"                           : "KSuite",
    "azure-activedirectory-library-for-python.git"            : "azure-activedirectory-library-for-python.git",
    "blpapi-python.git"                                       : "Global Gas",
    "bom-vs-boy-vs-cal"                                       : "Global Gas",
    "calendar-migration.git"                                  : "KSuite",
    "catalog-api-service.git"                                 : "KSuite",
    "catalog-external-loader.git"                             : "KSuite",
    "catalog-query-api-service.git"                           : "KSuite",
    "cce-coded-curves.git"                                    : "KSuite",
    "colonialcycleinterp.git"                                 : "KSuite",
    "core-infrastructure-mongodb.git"                         : "KSuite",
    "coreds-event-pipeline-batch-distributor.git"             : "MarketData (legacy)",
    "coreds-event-pipeline-kcall-interceptor.git"             : "MarketData (legacy)",
    "coreds-event-pipeline-structure-node-consumer.git"       : "MarketData (legacy)",
    "data-pipeline-schemas.git"                               : "MarketData (legacy)",
    "data-subscription-definitions.git"                       : "MarketData (legacy)",
    "dataframe-engine-service.git"                            : "MarketData (legacy)",
    "datasnapper.git"                                         : "MarketData (legacy)",
    "distribution-check-conti"                                : "KSuite",
    "distribution-manager-service.git"                        : "KSuite",
    "distributions-manager-service-deployment.git"            : "KSuite",
    "distributions-work-dispatcher-service.git"               : "KSuite",
    "dockerawspythonexplore.git"                              : "Scratches",
    "drc-evaluation-api-service.git"                          : "KSuite",
    "drc-ui-api-service.git"                                  : "KSuite",
    "drm-coreds-database-changes"                             : "KSuite",
    "drm-drc-migration"                                       : "KSuite",
    "eu-td-aggregator"                                        : "Global Gas",
    "eu-wind-aggregator"                                      : "Global Gas",
    "eua-switch-prices"                                       : "Global Gas",
    "european-black-scholes-76-xll.git"                       : "Global Gas",
    "european-black-scholes-76.git"                           : "Global Gas",
    "front-month-analysis"                                    : "Global Gas",
    "front-week-analysis"                                     : "Global Gas",
    "gas-level-overview"                                      : "Global Gas",
    "gas-storage-gse"                                         : "Global Gas",
    "generic-stack"                                           : "Tools",
    "git-commands.git"                                        : "Tools",
    "gundies-to-ksuite-data-service.git"                      : "Gundies",
    "gundies-to-ksuite-data-service.wiki.git"                 : "Gundies",
    "iam-roles.git"                                           : "KSuite",
    "kcalc-api-service-3-deployment.git"                      : "KSuite",
    "kcalc-api-service-3.git"                                 : "KSuite",
    "kcalc-calculation-dispatcher"                            : "KSuite",
    "kcalc-calculation-dispatcher-3-deployment.git"           : "KSuite",
    "kcalc-calculation-dispatcher-3.git"                      : "KSuite",
    "kcalc-calculation-dispatcher.git"                        : "KSuite",
    "kcalc-calculation-manager-3-deployment.git"              : "KSuite",
    "kcalc-calculation-manager-3.git"                         : "KSuite",
    "kcalc-calculation-manager.git"                           : "KSuite",
    "kcalc-cli-integration-tests.git"                         : "KSuite",
    "kcalc-coded-curves.git"                                  : "KSuite",
    "kcalc-core"                                              : "KSuite",
    "kcalc-coreds-legacy-event-pump"                          : "KSuite",
    "kcalc-coreds-legacy-event-pump.git"                      : "KSuite",
    "kcalc-custom-code-runner-deployment.git"                 : "KSuite",
    "kcalc-custom-code-runner.git"                            : "KSuite",
    "kcalc-data-model-3.git"                                  : "KSuite",
    "kcalc-dependency-evaluator"                              : "KSuite",
    "kcalc-engine-infrastructure.git"                         : "KSuite",
    "kcalc-infrastructure.git"                                : "KSuite",
    "kcalc-kquery-api-gateway"                                : "KSuite",
    "kcalc-kquery-bridge"                                     : "KSuite",
    "kcalc-module-options-volatility.git"                     : "KSuite",
    "kcalc-modules-3.git"                                     : "KSuite",
    "kcalc-modules.git"                                       : "KSuite",
    "kcalc-published-curves-service.git"                      : "KSuite",
    "kcalc-python-coded-curve-workbench.git"                  : "KSuite",
    "kcalc-result-legacy-loader.git"                          : "KSuite",
    "kcalc-test-helper.git"                                   : "KSuite",
    "kcalc-ui-api-service.git"                                : "KSuite",
    "kcalc-ui.git"                                            : "KSuite",
    "kcalc-user-settings-service.git"                         : "KSuite",
    "kcalc-workspace-service.git"                             : "KSuite",
    "kcalc3-utilities.git"                                    : "KSuite",
    "kochid-cli.git"                                          : "Tools",
    "kquery-api-service.git"                                  : "KSuite",
    "kquery-api.git"                                          : "KSuite",
    "kquery-core.git"                                         : "KSuite",
    "kquery-core.wiki.git"                                    : "KSuite",
    "kquery-engine-service.git"                               : "KSuite",
    "kquery-excel-addin.git"                                  : "KSuite",
    "kquery-gui-api.git"                                      : "KSuite",
    "kquery-single-series"                                    : "KSuite",
    "kquery-test-data.git"                                    : "KSuite",
    "kquery-ui-api-service.git"                               : "KSuite",
    "ksuite-cli.git"                                          : "KSuite",
    "ksuite-cloud-docs"                                       : "KSuite",
    "ksuite-cloud-planning.wiki.git"                          : "KSuite",
    "ksuite-datastore-controller.git"                         : "KSuite",
    "ksuite-lambda-app.git"                                   : "KSuite",
    "ksuite-period-codes.git"                                 : "KSuite",
    "ksuite-structure-data-pipeline"                          : "KSuite",
    "ksuitedotnet.git"                                        : "KSuite",
    "ksuitepy.git"                                            : "KSuite",
    "live-dashboard.git"                                      : "Global Gas",
    "live-positions.git"                                      : "Global Gas",
    "lng-fundamentals.git"                                    : "Global Gas",
    "lng-marking.git"                                         : "Global Gas",
    "lng-prices.git"                                          : "Global Gas",
    "lng-terminal-tracker.git"                                : "Global Gas",
    "lng-terminals.git"                                       : "Global Gas",
    "lng-yoy-report.git"                                      : "Global Gas",
    "morning-prompt-analysis"                                 : "Global Gas",
    "nelder-mead-simplex.git"                                 : "Global Gas",
    "ngbasisplusdiff.git"                                     : "Global Gas",
    "options-package-validation.git"                          : "Global Gas",
    "pricing-xl-add-in.git"                                   : "Global Gas",
    "pwr-prompt-dashboard"                                    : "Global Gas",
    "pwr-prompt-thermal-demand"                               : "Global Gas",
    "pwr-st-stack-model"                                      : "Global Gas",
    "py_vollib.git"                                           : "Global Gas",
    "pycurvebuilder.git"                                      : "KSuite",
    "pyhellotest.git"                                         : "Scratches",
    "python3-connect-rest-sample.git"                         : "Scratches",
    "pythonexploratory.git"                                   : "Scratches",
    "r-install.ps.git"                                        : "Tools",
    "run-pwr-dashboards-am"                                   : "Global Gas",
    "sandboxing.git"                                          : "Scratches",
    "schema-definitions.git"                                  : "KSuite",
    "secrets.ps.git"                                          : "Scratches",
    "smop.git"                                                : "Global Gas",
    "sparks-and-darks-lp"                                     : "Global Gas",
    "starfish-cxl-sql.git"                                    : "Global Gas",
    "storage-levels.git"                                      : "Global Gas",
    "storageoptimizationaddin.git"                            : "CXL.GlobalGasOptimization",
    "structure-api-service-deployment.git"                    : "KSuite",
    "structure-api-service.git"                               : "KSuite",
    "structure-data-pipeline-async-consumer.git"              : "KSuite",
    "structure-data-pipeline-service.git"                     : "KSuite",
    "structure-data-pipeline-workflow-manager.git"            : "KSuite",
    "structure-datastore-controller-daterange-partitioner.git": "KSuite",
    "structure-datastore-controller-single-partitioner.git"   : "KSuite",
    "structure-datastore-events-publisher.git"                : "KSuite",
    "subscription_service.git"                                : "KSuite",
    "tpt-options-pricing.git"                                 : "CXL",
    "transportation-forward.git"                              : "KSuite",
    "wkday-wkend-base-peak"                                   : "KSuite"
}

aggregated = aggregate_projects(data, mapping)
with open('a:\git_status\git_status_aggregated.json', 'w', encoding='utf-8') as fo:
    fo.write(json.dumps(aggregated, indent=2, default=str))

# print(json.dumps({k: k for k in sorted((k for k in aggregated.keys()))}, indent=2, default=str))
with open('a:\git_status\git_status_aggregated.md', 'w', encoding='utf-8') as fo:
    fo.write(build_md_from_agged(aggregated))
